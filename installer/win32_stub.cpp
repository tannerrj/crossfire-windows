#include <windows.h>
#include <winsvc.h>
#include <stdio.h>
#include <stdlib.h>

int bRunning = 1;

static SERVICE_STATUS        g_Status;
static SERVICE_STATUS_HANDLE g_StatusHandle;

#define SERVICE_NAME    L"CrossfireServer"
#define SERVICE_DISPLAY L"Crossfire Server"
#define SERVICE_DESC    L"Crossfire RPG multiplayer server"
#define REG_INSTALL_KEY L"Software\\Crossfire Server"
#define REG_INSTALL_VAL L"InstallDir"

static void WINAPI ServiceCtrlHandler(DWORD ctrl) {
    if (ctrl == SERVICE_CONTROL_STOP) {
        g_Status.dwCurrentState = SERVICE_STOP_PENDING;
        SetServiceStatus(g_StatusHandle, &g_Status);
        bRunning = 0;
    }
}

extern int main(int argc, char **argv);

static void WINAPI ServiceMain(DWORD argc, LPTSTR *argv) {
    g_Status.dwServiceType             = SERVICE_WIN32_OWN_PROCESS;
    g_Status.dwCurrentState            = SERVICE_START_PENDING;
    g_Status.dwControlsAccepted        = SERVICE_ACCEPT_STOP;
    g_Status.dwWin32ExitCode           = 0;
    g_Status.dwServiceSpecificExitCode = 0;
    g_Status.dwCheckPoint              = 0;
    g_Status.dwWaitHint                = 0;

    g_StatusHandle = RegisterServiceCtrlHandlerW(SERVICE_NAME, ServiceCtrlHandler);
    if (!g_StatusHandle) return;

    g_Status.dwCurrentState = SERVICE_RUNNING;
    SetServiceStatus(g_StatusHandle, &g_Status);

    /* Read install dir from registry (written by NSIS at install time). */
    wchar_t installDirW[MAX_PATH] = L"";
    HKEY hKey;
    if (RegOpenKeyExW(HKEY_LOCAL_MACHINE, REG_INSTALL_KEY, 0, KEY_READ, &hKey) == ERROR_SUCCESS) {
        DWORD size = sizeof(installDirW);
        RegQueryValueExW(hKey, REG_INSTALL_VAL, NULL, NULL, (LPBYTE)installDirW, &size);
        RegCloseKey(hKey);
    }

    /* Fallback: derive from exe path (exe lives at INSTDIR\bin\). */
    if (installDirW[0] == L'\0') {
        GetModuleFileNameW(NULL, installDirW, MAX_PATH);
        wchar_t *slash = wcsrchr(installDirW, L'\\');
        if (slash) *slash = L'\0'; /* strip exe name → INSTDIR\bin */
        slash = wcsrchr(installDirW, L'\\');
        if (slash) *slash = L'\0'; /* strip \bin → INSTDIR */
    }

    char installDir[MAX_PATH];
    WideCharToMultiByte(CP_ACP, 0, installDirW, -1, installDir, MAX_PATH, NULL, NULL);

    /* Set Python environment so cfpython.dll can find the stdlib. */
    char pythonHome[MAX_PATH];
    char pythonPath[MAX_PATH * 2];
    snprintf(pythonHome, MAX_PATH, "%s", installDir);
    snprintf(pythonPath, MAX_PATH * 2, "%s\\lib\\python3.14;%s\\lib\\python3.14\\lib-dynload",
             installDir, installDir);
    SetEnvironmentVariableA("PYTHONHOME", pythonHome);
    SetEnvironmentVariableA("PYTHONPATH", pythonPath);

    /* Add bin\ to DLL search path. */
    char binDir[MAX_PATH];
    snprintf(binDir, MAX_PATH, "%s\\bin", installDir);
    SetDllDirectoryA(binDir);

    /* Build absolute paths for -data, -conf, -local. */
    static char data[MAX_PATH], conf[MAX_PATH], local_[MAX_PATH];
    snprintf(data,   MAX_PATH, "%s\\share\\crossfire", installDir);
    snprintf(conf,   MAX_PATH, "%s\\etc\\crossfire",   installDir);

    char programData[MAX_PATH] = "C:\\ProgramData";
    GetEnvironmentVariableA("ProgramData", programData, MAX_PATH);
    snprintf(local_, MAX_PATH, "%s\\Crossfire Server", programData);

    static char *svcArgv[] = {
        (char *)"crossfire-server",
        (char *)"-data",  data,
        (char *)"-conf",  conf,
        (char *)"-local", local_,
        (char *)"-p",     (char *)"13327",
        NULL
    };
    main(9, svcArgv);

    g_Status.dwCurrentState = SERVICE_STOPPED;
    SetServiceStatus(g_StatusHandle, &g_Status);
}

void service_register(void) {
    wchar_t exePath[MAX_PATH];
    GetModuleFileNameW(NULL, exePath, MAX_PATH);

    /* BinaryPathName: "path\crossfire-server.exe" -srv */
    wchar_t cmdLine[MAX_PATH + 8];
    swprintf(cmdLine, MAX_PATH + 8, L"\"%ls\" -srv", exePath);

    SC_HANDLE scm = OpenSCManagerW(NULL, NULL, SC_MANAGER_CREATE_SERVICE);
    if (!scm) {
        printf("OpenSCManager failed: %lu\n", GetLastError());
        exit(1);
    }

    SC_HANDLE svc = CreateServiceW(scm,
        SERVICE_NAME,
        SERVICE_DISPLAY,
        SERVICE_ALL_ACCESS,
        SERVICE_WIN32_OWN_PROCESS,
        SERVICE_AUTO_START,
        SERVICE_ERROR_NORMAL,
        cmdLine,
        NULL, NULL, NULL, NULL, NULL);

    if (!svc) {
        printf("CreateService failed: %lu\n", GetLastError());
        CloseServiceHandle(scm);
        exit(1);
    }

    SERVICE_DESCRIPTIONW desc = { (LPWSTR)SERVICE_DESC };
    ChangeServiceConfig2W(svc, SERVICE_CONFIG_DESCRIPTION, &desc);

    CloseServiceHandle(svc);
    CloseServiceHandle(scm);
    printf("Service registered. Start it via Services or: sc start CrossfireServer\n");
    exit(0);
}

void service_unregister(void) {
    SC_HANDLE scm = OpenSCManagerW(NULL, NULL, SC_MANAGER_ALL_ACCESS);
    if (!scm) {
        printf("OpenSCManager failed: %lu\n", GetLastError());
        exit(1);
    }

    SC_HANDLE svc = OpenServiceW(scm, SERVICE_NAME, SERVICE_STOP | DELETE | SERVICE_QUERY_STATUS);
    if (!svc) {
        printf("Service not found.\n");
        CloseServiceHandle(scm);
        exit(0);
    }

    /* Stop the service if it is running. */
    SERVICE_STATUS status;
    if (QueryServiceStatus(svc, &status) && status.dwCurrentState != SERVICE_STOPPED) {
        ControlService(svc, SERVICE_CONTROL_STOP, &status);
        Sleep(2000);
    }

    if (!DeleteService(svc))
        printf("DeleteService failed: %lu\n", GetLastError());
    else
        printf("Service unregistered.\n");

    CloseServiceHandle(svc);
    CloseServiceHandle(scm);
    exit(0);
}

void service_handle(void) {
    SERVICE_TABLE_ENTRYW table[] = {
        { (LPWSTR)SERVICE_NAME, ServiceMain },
        { NULL, NULL }
    };
    StartServiceCtrlDispatcherW(table);
    exit(0);
}
