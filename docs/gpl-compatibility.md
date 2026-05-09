# GPLv2 Compatibility Analysis

All changes in this repository are fully compatible with GPLv2.

## Summary

Every modification is either a bug fix, a platform portability shim,
or a Windows API call replacing an equivalent POSIX call. No
incompatibly-licensed code was introduced.

## Key Points

- Windows API calls (`MoveFileExA`, `FindFirstFileA`, `WSAGetLastError` etc.)
  are covered by GPLv2's system library exception.
- The `ffs()` implementation uses a GCC compiler intrinsic, not a library.
- MinGW runtime DLLs are licensed under the GCC Runtime Library Exception,
  which explicitly permits use with GPLv2 software.
- `libpython3.14.dll` is under the Python Software Foundation License,
  which is GPLv2 compatible.
- No copyright notices or license headers were modified.

## Full Analysis

See the project documentation for a file-by-file GPLv2 compatibility
analysis of each patch.
