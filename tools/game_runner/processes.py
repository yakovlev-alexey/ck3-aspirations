"""Bounded worker ownership using a Windows kill-on-close Job."""
import ctypes
import json
import os
import subprocess
import time
from ctypes import wintypes


class WorkerCleanupError(RuntimeError):
    pass


class ProcessJob:
    def __init__(self):
        if os.name != 'nt':
            raise RuntimeError('Managed sessions require Windows process jobs')
        self.api = ctypes.WinDLL('kernel32', use_last_error=True)
        self.api.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        self.api.CreateJobObjectW.restype = wintypes.HANDLE
        self.api.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
        self.api.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        self.api.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
        self.api.QueryInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p]
        self.api.CloseHandle.argtypes = [wintypes.HANDLE]
        self.api.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        self.api.OpenProcess.restype = wintypes.HANDLE
        self.api.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        self.api.IsProcessInJob.argtypes = [wintypes.HANDLE, wintypes.HANDLE, ctypes.POINTER(wintypes.BOOL)]
        self.handle = self.api.CreateJobObjectW(None, None)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        class Basic(ctypes.Structure):
            _fields_ = [('process_time', ctypes.c_longlong), ('job_time', ctypes.c_longlong), ('flags', wintypes.DWORD), ('minimum', ctypes.c_size_t), ('maximum', ctypes.c_size_t), ('active_limit', wintypes.DWORD), ('affinity', ctypes.c_size_t), ('priority', wintypes.DWORD), ('scheduling', wintypes.DWORD)]
        class IO(ctypes.Structure):
            _fields_ = [(name, ctypes.c_ulonglong) for name in ('read_ops', 'write_ops', 'other_ops', 'read_bytes', 'write_bytes', 'other_bytes')]
        class Extended(ctypes.Structure):
            _fields_ = [('basic', Basic), ('io', IO), ('process_memory', ctypes.c_size_t), ('job_memory', ctypes.c_size_t), ('peak_process', ctypes.c_size_t), ('peak_job', ctypes.c_size_t)]
        limits = Extended()
        limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self.api.SetInformationJobObject(self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
            self.api.CloseHandle(self.handle)
            self.handle = None
            raise ctypes.WinError(ctypes.get_last_error())

    def assign(self, process):
        if not self.api.AssignProcessToJobObject(self.handle, int(process._handle)):
            raise ctypes.WinError(ctypes.get_last_error())

    def close(self):
        if self.handle is None:
            return
        class Accounting(ctypes.Structure):
            _fields_ = [('user', ctypes.c_longlong), ('kernel', ctypes.c_longlong), ('period_user', ctypes.c_longlong), ('period_kernel', ctypes.c_longlong), ('faults', wintypes.DWORD), ('total', wintypes.DWORD), ('active', wintypes.DWORD), ('terminated', wintypes.DWORD)]
        handles = []
        try:
            class ProcessList(ctypes.Structure):
                _fields_ = [('assigned', wintypes.DWORD), ('listed', wintypes.DWORD), ('pids', ctypes.c_size_t * 1024)]
            processes = ProcessList()
            if not self.api.QueryInformationJobObject(self.handle, 3, ctypes.byref(processes), ctypes.sizeof(processes), None):
                raise ctypes.WinError(ctypes.get_last_error())
            for pid in processes.pids[:processes.listed]:
                handle = self.api.OpenProcess(0x100000 | 0x1000, False, pid)
                if handle:
                    owned = wintypes.BOOL()
                    if not self.api.IsProcessInJob(handle, self.handle, ctypes.byref(owned)):
                        self.api.CloseHandle(handle)
                        raise ctypes.WinError(ctypes.get_last_error())
                    if owned.value:
                        handles.append(handle)
                    else:
                        self.api.CloseHandle(handle)
            if not self.api.TerminateJobObject(self.handle, 1):
                raise ctypes.WinError(ctypes.get_last_error())
            deadline = time.monotonic() + 5
            for handle in handles:
                remaining_ms = max(0, int((deadline - time.monotonic()) * 1000))
                if self.api.WaitForSingleObject(handle, remaining_ms) != 0:
                    raise RuntimeError('Owned process exit was not signaled')
            while True:
                state = Accounting()
                if not self.api.QueryInformationJobObject(self.handle, 1, ctypes.byref(state), ctypes.sizeof(state), None):
                    raise ctypes.WinError(ctypes.get_last_error())
                if state.active == 0:
                    return
                if time.monotonic() >= deadline:
                    raise RuntimeError('Owned job processes did not exit; do not restore a live profile')
                time.sleep(0.05)
        finally:
            for handle in handles:
                self.api.CloseHandle(handle)
            self.api.CloseHandle(self.handle)
            self.handle = None


def supervise_worker(command, cwd, timeout, audit_path=None):
    job = ProcessJob()
    process = None
    audit = {"job_assigned": False, "processes_stopped": False}
    try:
        process = subprocess.Popen(command, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        # Worker cannot launch CK3 until assignment succeeds and stdin releases it.
        job.assign(process)
        audit.update({"job_assigned": True, "worker_pid": process.pid})
        if audit_path is not None:
            audit_path.write_text(json.dumps(audit), encoding="utf-8")
        try:
            output, errors = process.communicate('go\n', timeout=timeout)
        except subprocess.TimeoutExpired as error:
            raise TimeoutError('Managed session deadline exceeded') from error
        if process.returncode != 0:
            raise RuntimeError('Managed worker failed: ' + errors[-2000:])
        return output
    finally:
        cleanup_error = None
        try:
            job.close()
            if process is not None and process.poll() is None:
                process.kill()
                process.wait(timeout=5)
            audit['processes_stopped'] = True
        except (RuntimeError, OSError, subprocess.TimeoutExpired) as error:
            cleanup_error = WorkerCleanupError('Owned process cleanup could not be confirmed: ' + str(error))
            raise cleanup_error from error
        finally:
            if audit_path is not None:
                try:
                    audit_path.write_text(json.dumps(audit), encoding='utf-8')
                except OSError as error:
                    if cleanup_error is not None:
                        raise WorkerCleanupError(str(cleanup_error) + '; process audit persistence failed: ' + str(error)) from cleanup_error
                    raise
