@echo off

set input2=%1
set input3=%2
set helpflag="%input2%"
set PRODUCT_DAM_INC=exs_tx
if "%input2%"=="-p" (
	:: echo "load special product config."
	if "%input3%"=="pls" (
		echo Begin to build product for pls.
		set PRODUCT_DAM_INC=pls
	) else if "%input3%"=="exs_tx" (
		echo Begin to build product for exs_tx.
		set PRODUCT_DAM_INC=exs_tx
	) else (
		echo Begin to build product for exs_tx.
		set PRODUCT_DAM_INC=exs_tx
	)
) else if "%input2%"=="-h" (
	echo Usage: build.bat [OPTIONS]...
	echo Execute Compiling Demo application.
	echo Parameter Description:
	echo   -h, Display this help and exit.
	echo   -p, -p=value The product supported value is exs_tx or pls.

	echo Usage example:
	echo   Perform Compiling for exs_tx:
	echo     .\build.bat -p exs_tx

	echo   Perform Compiling for pls:
	echo     .\build.bat -p pls
	goto help
) else (
	echo Begin to build product for exs_tx.
	set PRODUCT_DAM_INC=exs_tx
)

set APPPATH=%3
set APPNAME=%4

set DAM_RO_BASE=0x42000000

set LLVM_ROOT_PATH=%EP_SDK_PATH%\tools\windows\llvm
set TOOLCHAIN_PATH=%LLVM_ROOT_PATH%\bin
set TOOLCHAIN_PATH_STANDARDS=%LLVM_ROOT_PATH%\armv7m-none-eabi\libc\include
set LLVMLIB=%LLVM_ROOT_PATH%\lib\clang\4.0.3\lib
set LLVMLINK_PATH=%LLVM_ROOT_PATH%\tools\bin
set DAM_INC_BASE=%EP_SDK_PATH%\common\include
set DAM_LIB_PATH=%EP_SDK_PATH%\common\libs
set DAM_SRC_PATH=%EP_SDK_PATH%\common\src
set PYTHON_PATH=%EP_PYTHON_PATH%\python.exe

set BUILD_PATH=build\%APPNAME%
set DAM_DAM_DEMO_LD_PATH=build

set DAM_LIBNAME=txm_lib.lib
set TIMER_LIBNAME=timer_dam_lib.lib
set DIAG_LIB_NAME=diag_dam_lib.lib
set QMI_LIB_NAME=qcci_dam_lib.lib
set QMI_QCCLI_LIB_NAME=IDL_DAM_LIB.lib

set DAM_ELF_NAME=%APPNAME%.elf
set DAM_TARGET_BIN=%APPNAME%.bin
set DAM_MAP_NAME=%APPNAME%.map

set CURRENT_PATH=%~dp0

if not exist %BUILD_PATH% (
  mkdir %BUILD_PATH%
)

echo %BUILD_PATH%

echo "Application RO base selected = %DAM_RO_BASE%"

if "%PRODUCT_DAM_INC%"=="pls" (
	set DAM_CPPFLAGS= -DUSER_CODE -DQAPI_TXM_MODULE -DTXM_MODULE -DGINA_TXM_MODULE -DTX_DAM_QC_CUSTOMIZATIONS -DTX_ENABLE_PROFILING -DTX_ENABLE_EVENT_TRACE -DTX_DISABLE_NOTIFY_CALLBACKS  -DFX_FILEX_PRESENT -DTX_ENABLE_IRQ_NESTING  -DTX3_CHANGES  -DPRODUCT_PLS
) else (
	set DAM_CPPFLAGS= -DUSER_CODE -DQAPI_TXM_MODULE -DTXM_MODULE -DGINA_TXM_MODULE -DTX_DAM_QC_CUSTOMIZATIONS -DTX_ENABLE_PROFILING -DTX_ENABLE_EVENT_TRACE -DTX_DISABLE_NOTIFY_CALLBACKS  -DFX_FILEX_PRESENT -DTX_ENABLE_IRQ_NESTING  -DTX3_CHANGES  -DPRODUCT_EXS_TX
)

set DAM_CFLAGS= -g -marm -target armv7m-none-musleabi -mfloat-abi=softfp -mfpu=none -mcpu=cortex-a7 -mno-unaligned-access  -fms-extensions -Osize -fshort-enums -Wbuiltin-macro-redefined

set DAM_INCPATHS=-I %DAM_INC_BASE% -I %DAM_INC_BASE%\threadx_api -I %DAM_INC_BASE%\threadx_api\%PRODUCT_DAM_INC% -I %DAM_INC_BASE%\qapi -I %DAM_INC_BASE%\qapi\%PRODUCT_DAM_INC% -I %DAM_INC_BASE%\gina -I %DAM_INC_BASE%\gina\%PRODUCT_DAM_INC% -I %TOOLCHAIN_PATH_STANDARDS% -I %LLVMLIB%


echo "Compiling Demo application"

copy %CURRENT_PATH%\template.ld %CURRENT_PATH%\%APPNAME%.ld

%TOOLCHAIN_PATH%\clang.exe -E  %DAM_CPPFLAGS% %DAM_CFLAGS% %CURRENT_PATH%\txm_module_preamble_llvm.S > %BUILD_PATH%\txm_module_preamble_llvm_pp.S

%TOOLCHAIN_PATH%\clang.exe  -c %DAM_CPPFLAGS% %DAM_CFLAGS% %BUILD_PATH%\txm_module_preamble_llvm_pp.S -o %BUILD_PATH%\txm_module_preamble_llvm.o

if %ERRORLEVEL%==0 goto proceed
if %ERRORLEVEL%==1 goto exit
:proceed

%TOOLCHAIN_PATH%\clang.exe -c %DAM_CPPFLAGS% %DAM_CFLAGS% %DAM_INCPATHS% %APPPATH%\*.c %DAM_SRC_PATH%\*.c

if %ERRORLEVEL%==0 (
echo "compilation succeed"
move *.o %BUILD_PATH%
echo "Linking Demo application"

%TOOLCHAIN_PATH%\clang++.exe -d -o %BUILD_PATH%\%DAM_ELF_NAME% -target armv7m-none-musleabi -fuse-ld=qcld -lc++ -Wl,-mno-unaligned-access -fuse-baremetal-sysroot -fno-use-baremetal-crt -Wl, %BUILD_PATH%\txm_module_preamble_llvm.o -Wl,-T%CURRENT_PATH%\%APPNAME%.ld -Wl,-Map=%BUILD_PATH%\%DAM_MAP_NAME%,-gc-sections -Wl,-gc-sections %BUILD_PATH%\*.o %DAM_LIB_PATH%\%PRODUCT_DAM_INC%\*.lib %DAM_LIB_PATH%\*.lib
%PYTHON_PATH% %LLVMLINK_PATH%\llvm-elf-to-hex.py --bin %BUILD_PATH%\%DAM_ELF_NAME% --output %BUILD_PATH%\%DAM_TARGET_BIN%

del /f /s /q %CURRENT_PATH%\%APPNAME%.ld

echo "Demo application is built at" %BUILD_PATH%\%DAM_TARGET_BIN%
)else (
echo "Fail to compile. Exiting...."
echo "compilation failed with errors"
EXIT /B %ERRORLEVEL%
:exit
EXIT /B %ERRORLEVEL%
)
