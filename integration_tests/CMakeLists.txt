cmake_minimum_required(VERSION 3.15 FATAL_ERROR)

project(lpython_tests C)

if (NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Debug
        CACHE STRING "Build type (Debug, Release)" FORCE)
endif ()
if (NOT (CMAKE_BUILD_TYPE STREQUAL "Debug" OR
        CMAKE_BUILD_TYPE STREQUAL "Release"))
    message("${CMAKE_BUILD_TYPE}")
    message(FATAL_ERROR "CMAKE_BUILD_TYPE must be one of: Debug, Release (current value: '${CMAKE_BUILD_TYPE}')")
endif ()

set(KIND no CACHE STRING "Type of Test")
set(FAST no CACHE BOOL "Run supported tests with --fast")

find_program(LPYTHON NAMES lpython)

execute_process(COMMAND ${LPYTHON} --get-rtl-header-dir
    OUTPUT_VARIABLE LPYTHON_RTL_HEADER_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
    )
execute_process(COMMAND ${LPYTHON} --get-rtl-dir
    OUTPUT_VARIABLE LPYTHON_RTL_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
    )

find_path(LPYTHON_RTLIB_DIR lfortran_intrinsics.h
    HINTS ${LPYTHON_RTL_HEADER_DIR})
find_library(LPYTHON_RTLIB_LIBRARY lpython_runtime_static
    HINTS ${LPYTHON_RTL_DIR})
add_library(lpython_rtlib INTERFACE IMPORTED)
set_property(TARGET lpython_rtlib PROPERTY INTERFACE_INCLUDE_DIRECTORIES
    ${LPYTHON_RTLIB_DIR})
set_property(TARGET lpython_rtlib PROPERTY INTERFACE_LINK_LIBRARIES
    ${LPYTHON_RTLIB_LIBRARY})
target_link_libraries(lpython_rtlib INTERFACE m)

if (PYTHON_LIBS_REQ)
    find_package(Python COMPONENTS Interpreter Development)
    execute_process(
        COMMAND "${Python_EXECUTABLE}"
        -c "import numpy; print(numpy.get_include())"
        OUTPUT_VARIABLE NUMPY_INCLUDE_DIR
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    message("\n")
    message("System has the Python development artifacts: ${Python_Development_FOUND}")
    message("The Python include directories: ${Python_INCLUDE_DIRS}")
    message("The Python libraries: ${Python_LIBRARIES}")
    message("The Python library directories: ${Python_LIBRARY_DIRS}")
    message("The Python runtime library directories: ${Python_RUNTIME_LIBRARY_DIRS}")
    message("Python version: ${Python_VERSION}")
    message("Numpy Include Directory: ${NUMPY_INCLUDE_DIR}")
endif()

enable_testing()

message("\n")
message("Configuration results")
message("---------------------")
message("C compiler      : ${CMAKE_C_COMPILER}")
message("Build type: ${CMAKE_BUILD_TYPE}")
if (CMAKE_BUILD_TYPE STREQUAL "Debug")
    message("C compiler flags      : ${CMAKE_C_FLAGS_DEBUG}")
else ()
    message("C compiler flags      : ${CMAKE_C_FLAGS_RELEASE}")
endif ()
message("Installation prefix: ${CMAKE_INSTALL_PREFIX}")
message("KIND: ${KIND}")
message("FAST: ${FAST}")
message("PYTHON_LIBS_REQ: ${PYTHON_LIBS_REQ}")
message("LPYTHON: ${LPYTHON}")
message("LPYTHON_RTLIB_DIR: ${LPYTHON_RTLIB_DIR}")
message("LPYTHON_RTLIB_LIBRARY: ${LPYTHON_RTLIB_LIBRARY}")


macro(RUN_UTIL RUN_FAIL RUN_NAME RUN_FILE_NAME RUN_LABELS RUN_EXTRAFILES RUN_NOMOD RUN_EXTRA_ARGS RUN_COPY_TO_BIN)
    set(fail ${${RUN_FAIL}})
    set(name ${${RUN_NAME}})
    set(file_name ${${RUN_FILE_NAME}})
    set(labels ${${RUN_LABELS}})
    set(extra_files ${${RUN_EXTRAFILES}})
    set(no_mod ${${RUN_NOMOD}})
    set(extra_args ${${RUN_EXTRA_ARGS}})
    set(copy_to_bin ${${RUN_COPY_TO_BIN}})

    if (NOT name)
        message(FATAL_ERROR "Must specify the NAME argument")
    endif()

    if (${KIND} IN_LIST labels)
        if (KIND STREQUAL "llvm")
            add_custom_command(
                OUTPUT ${name}.o
                COMMAND ${LPYTHON} -c ${extra_args} ${CMAKE_CURRENT_SOURCE_DIR}/${file_name}.py -o ${name}.o
                DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/${file_name}.py
                VERBATIM)
            add_executable(${name} ${name}.o ${extra_files})
            set_target_properties(${name} PROPERTIES LINKER_LANGUAGE C)
            target_link_libraries(${name} lpython_rtlib)
            add_test(${name} ${CMAKE_CURRENT_BINARY_DIR}/${name})
            if (labels)
                set_tests_properties(${name} PROPERTIES LABELS "${labels}")
            endif()
            if (${fail})
                set_tests_properties(${name} PROPERTIES WILL_FAIL TRUE)
            endif()
        elseif (KIND STREQUAL "llvm_jit")
            add_test(
                NAME ${name}
                COMMAND ${LPYTHON} --jit ${extra_args} ${CMAKE_CURRENT_SOURCE_DIR}/${file_name}.py)
            if (labels)
                set_tests_properties(${name} PROPERTIES LABELS "${labels}")
            endif()
            if (${fail})
                set_tests_properties(${name} PROPERTIES WILL_FAIL TRUE)
            endif()
        elseif (KIND STREQUAL "llvm_py")
            add_custom_command(
                OUTPUT ${name}.o
                COMMAND ${LPYTHON} -c ${extra_args} ${CMAKE_CURRENT_SOURCE_DIR}/${file_name}.py -o ${name}.o
                DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/${file_name}.py
                VERBATIM)
            add_executable(${name} ${name}.o ${extra_files})
            target_include_directories(${name} PRIVATE ${CMAKE_SOURCE_DIR} ${NUMPY_INCLUDE_DIR})
            set_target_properties(${name} PROPERTIES LINKER_LANGUAGE C)
            target_link_libraries(${name} lpython_rtlib Python::Python)
            add_test(${name} ${CMAKE_CURRENT_BINARY_DIR}/${name})
            if (labels)
                set_tests_properties(${name} PROPERTIES LABELS "${labels}")
            endif()
            if (${fail})
                set_tests_properties(${name} PROPERTIES WILL_FAIL TRUE)
            endif()
        elseif(KIND STREQUAL "llvm_sym")
            add_custom_command(
                OUTPUT ${name}.o
                COMMAND ${LPYTHON} -c ${extra_args} ${CMAKE_CURRENT_SOURCE_DIR}/${file_name}.py -o ${name}.o
                DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/${file_name}.py
                VERBATIM)
            add_executable(${name} ${name}.o ${extra_files})
            set_target_properties(${name} PROPERTIES LINKER_LANGUAGE C)
            if (APPLE)
                set(SYMENGINE_LIB "${Python_LIBRARY_DIRS}/libsymengine.dylib")
            else()
                set(SYMENGINE_LIB "${Python_LIBRARY_DIRS}/libsymengine.so")
            endif()
            target_link_libraries(${name} lpython_rtlib ${SYMENGINE_LIB})
            add_test(${name} ${CMAKE_CURRENT_BINARY_DIR}/${name})
            if (labels)
                set_tests_properties(${name} PROPERTIES LABELS "${labels}")
            endif()
            if (${fail})
                set_tests_properties(${name} PROPERTIES WILL_FAIL TRUE)
            endif()
        elseif(KIND STREQUAL "c")
            add_custom_command(
                OUTPUT ${name}.c
                COMMAND ${LPYTHON} ${extra_args} --show-c ${CMAKE_CURRENT_SOURCE_DIR}/${file_name}.py > ${name}.c
                DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/${file_name}.py
                VERBATIM)
            add_executable(${name} ${name}.c ${extra_files})
            target_include_directories(${name} PRIVATE ${CMAKE_SOURCE_DIR})
            set_target_properties(${name} PROPERTIES LINKER_LANGUAGE C)
            target_link_libraries(${name} lpython_rtlib)
            add_test(${name} ${CMAKE_CURRENT_BINARY_DIR}/${name})
            if (labels)
                set_tests_properties(${name} PROPERTIES LABELS "${labels}")
            endif()
            if (${fail})
                set_tests_properties(${name} PROPERTIES WILL_FAIL TRUE)
            endif()
        elseif(KIND STREQUAL "c_py")
            add_custom_command(
                OUTPUT ${name}.c
                COMMAND ${LPYTHON} ${extra_args} --show-c ${CMAKE_CURRENT_SOURCE_DIR}/${file_name}.py > ${name}.c
                DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/${file_name}.py
                VERBATIM)
            add_executable(${name} ${name}.c ${extra_files})
            target_include_directories(${name} PRIVATE ${CMAKE_SOURCE_DIR} ${NUMPY_INCLUDE_DIR})
            set_target_properties(${name} PROPERTIES LINKER_LANGUAGE C)
            target_link_libraries(${name} lpython_rtlib Python::Python)
            add_test(${name} ${CMAKE_CURRENT_BINARY_DIR}/${name})
            if (labels)
                set_tests_properties(${name} PROPERTIES LABELS "${labels}")
            endif()
            if (${fail})
                set_tests_properties(${name} PROPERTIES WILL_FAIL TRUE)
            endif()
        elseif(KIND STREQUAL "c_sym")
            add_custom_command(
                OUTPUT ${name}.c
                COMMAND ${LPYTHON} ${extra_args} --show-c
                    ${CMAKE_CURRENT_SOURCE_DIR}/${file_name}.py > ${name}.c
                DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/${file_name}.py
                VERBATIM)
            add_executable(${name} ${name}.c ${extra_files})
            target_include_directories(${name} PRIVATE ${CMAKE_SOURCE_DIR}
                "${Python_INCLUDE_DIRS}/..")
            set_target_properties(${name} PROPERTIES LINKER_LANGUAGE C)
            if (APPLE)
                set(SYMENGINE_LIB "${Python_LIBRARY_DIRS}/libsymengine.dylib")
            else()
                set(SYMENGINE_LIB "${Python_LIBRARY_DIRS}/libsymengine.so")
            endif()
            target_link_libraries(${name} lpython_rtlib ${SYMENGINE_LIB})
            add_test(${name} ${CMAKE_CURRENT_BINARY_DIR}/${name})
            if (labels)
                set_tests_properties(${name} PROPERTIES LABELS "${labels}")
            endif()
            if (${fail})
                set_tests_properties(${name} PROPERTIES WILL_FAIL TRUE)
            endif()
        elseif((KIND STREQUAL "cpython") OR (KIND STREQUAL "cpython_sym"))
            # CPython test
            if (extra_files)
                set(PY_MOD "${name}_mod")
                add_library(${PY_MOD} SHARED ${extra_files})
                set_target_properties(${PY_MOD} PROPERTIES LINKER_LANGUAGE C)
            else()
                set(PY_MOD "")
            endif()

            add_test(${name} python ${CMAKE_CURRENT_SOURCE_DIR}/${file_name}.py)
            if (no_mod)
                set_tests_properties(${name} PROPERTIES
                    ENVIRONMENT "PYTHONPATH=${CMAKE_SOURCE_DIR}/../src/runtime/lpython:${CMAKE_SOURCE_DIR}/..")
            else()
                set_tests_properties(${name} PROPERTIES
                    ENVIRONMENT "PYTHONPATH=${CMAKE_SOURCE_DIR}/../src/runtime/lpython:${CMAKE_SOURCE_DIR}/..;LPYTHON_PY_MOD_NAME=${PY_MOD};LPYTHON_PY_MOD_PATH=${CMAKE_CURRENT_BINARY_DIR}")
            endif()
            if (labels)
                set_tests_properties(${name} PROPERTIES LABELS "${labels}")
            endif()
            if (${fail})
                set_tests_properties(${name} PROPERTIES WILL_FAIL TRUE)
            endif()
        elseif(KIND STREQUAL "x86")
            # x86 test
            add_custom_command(
                OUTPUT ${name}.x86
                COMMAND ${LPYTHON} ${extra_args} --backend x86 ${CMAKE_CURRENT_SOURCE_DIR}/${file_name}.py -o ${name}.x86
                DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/${file_name}.py
                VERBATIM
            )
            add_custom_target(${name} ALL
            DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/${name}.x86)
            add_test(${name} ${CMAKE_CURRENT_BINARY_DIR}/${name}.x86)
            if (labels)
                set_tests_properties(${name} PROPERTIES LABELS "${labels}")
            endif()
            if (${fail})
                set_tests_properties(${name} PROPERTIES WILL_FAIL TRUE)
            endif()
        elseif(KIND STREQUAL "wasm_x86")
            # wasm_to_x86 test
            add_custom_command(
                OUTPUT ${name}.x86
                COMMAND ${LPYTHON} ${extra_args} --backend wasm_x86 ${CMAKE_CURRENT_SOURCE_DIR}/${file_name}.py -o ${name}.x86
                DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/${file_name}.py
                VERBATIM
            )
            add_custom_target(${name} ALL
            DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/${name}.x86)
            add_test(${name} ${CMAKE_CURRENT_BINARY_DIR}/${name}.x86)
            if (labels)
                set_tests_properties(${name} PROPERTIES LABELS "${labels}")
            endif()
            if (${fail})
                set_tests_properties(${name} PROPERTIES WILL_FAIL TRUE)
            endif()
        elseif(KIND STREQUAL "wasm_x64")
            # wasm_to_x64 test
            add_custom_command(
                OUTPUT ${name}.x64
                COMMAND ${LPYTHON} ${extra_args} --backend wasm_x64 ${CMAKE_CURRENT_SOURCE_DIR}/${file_name}.py -o ${name}.x64
                DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/${file_name}.py
                VERBATIM
            )
            add_custom_target(${name} ALL
            DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/${name}.x64)
            add_test(${name} ${CMAKE_CURRENT_BINARY_DIR}/${name}.x64)
            if (labels)
                set_tests_properties(${name} PROPERTIES LABELS "${labels}")
            endif()
            if (${fail})
                set_tests_properties(${name} PROPERTIES WILL_FAIL TRUE)
            endif()
        elseif(KIND STREQUAL "wasm")
            # wasm test
            execute_process(COMMAND ${LPYTHON} ${extra_args} --backend wasm ${CMAKE_CURRENT_SOURCE_DIR}/${file_name}.py -o ${name})

            find_program(WASM_EXEC_RUNTIME node)
            execute_process(COMMAND "${WASM_EXEC_RUNTIME}" --version
                            OUTPUT_VARIABLE WASM_EXEC_VERSION
                            OUTPUT_STRIP_TRAILING_WHITESPACE)

            string(REGEX REPLACE "v([0-9]+)\\.([0-9]+)\\.([0-9]+)" "\\1" NODE_MAJOR_VERSION "${WASM_EXEC_VERSION}")

            if (NODE_MAJOR_VERSION LESS 16)
                message(STATUS "${WASM_EXEC_RUNTIME} version: ${WASM_EXEC_VERSION}")
                set(WASM_EXEC_FLAGS "--experimental-wasm-bigint")
            endif()
            set(WASM_EXEC_FLAGS ${WASM_EXEC_FLAGS} "--experimental-wasi-unstable-preview1")
            add_test(${name} ${WASM_EXEC_RUNTIME} ${WASM_EXEC_FLAGS} ${CMAKE_CURRENT_BINARY_DIR}/${name}.js)
            if (labels)
                set_tests_properties(${name} PROPERTIES LABELS "${labels}")
            endif()
            if (${fail})
                set_tests_properties(${name} PROPERTIES WILL_FAIL TRUE)
            endif()
        endif()

        if (copy_to_bin)
            file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/${copy_to_bin} DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
        endif()

    endif()
endmacro(RUN_UTIL)

macro(RUN)
    set(options FAIL NOFAST NOMOD)
    set(oneValueArgs NAME IMPORT_PATH COPY_TO_BIN REQ_PY_VER)
    set(multiValueArgs LABELS EXTRAFILES EXTRA_ARGS)
    cmake_parse_arguments(RUN "${options}" "${oneValueArgs}"
                        "${multiValueArgs}" ${ARGN} )

    set(RUN_FILE_NAME ${RUN_NAME})

    if (RUN_IMPORT_PATH)
        # Only one import path supported for now
        # Later add support for multiple import paths by looping over and appending to extra args
        set(RUN_EXTRA_ARGS ${RUN_EXTRA_ARGS} -I${CMAKE_CURRENT_SOURCE_DIR}/${RUN_IMPORT_PATH})
    endif()

    if (RUN_REQ_PY_VER)
        string(REGEX REPLACE "([0-9]+)\\.([0-9]+)\\.([0-9]+)" "\\1" PY_MAJOR_VERSION "${Python_VERSION}")
        string(REGEX REPLACE "([0-9]+)\\.([0-9]+)\\.([0-9]+)" "\\2" PY_MINOR_VERSION "${Python_VERSION}")
        string(REGEX REPLACE "([0-9]+)\\.([0-9]+)" "\\1" REQ_PY_MAJOR_VERSION "${RUN_REQ_PY_VER}")
        string(REGEX REPLACE "([0-9]+)\\.([0-9]+)" "\\2" REQ_PY_MINOR_VERSION "${RUN_REQ_PY_VER}")

        if (PY_MINOR_VERSION LESS REQ_PY_MINOR_VERSION)
            # remove backends from the test that depend on CPython
            list(REMOVE_ITEM RUN_LABELS cpython cpython_sym c_py c_sym llvm_sym llvm_py)
        endif()
    endif()

    if (NOT FAST)
        RUN_UTIL(RUN_FAIL RUN_NAME RUN_FILE_NAME RUN_LABELS RUN_EXTRAFILES RUN_NOMOD RUN_EXTRA_ARGS RUN_COPY_TO_BIN)
    endif()

    if ((FAST) AND (NOT RUN_NOFAST))
        set(RUN_EXTRA_ARGS ${RUN_EXTRA_ARGS} --fast)
        set(RUN_NAME "${RUN_NAME}_FAST")
        list(REMOVE_ITEM RUN_LABELS cpython cpython_sym) # remove cpython, cpython_sym, from --fast test
        RUN_UTIL(RUN_FAIL RUN_NAME RUN_FILE_NAME RUN_LABELS RUN_EXTRAFILES RUN_NOMOD RUN_EXTRA_ARGS RUN_COPY_TO_BIN)
    endif()
endmacro(RUN)

# only compiles till object file
# to make sure that the generated code is syntactically correct
# but we cannot generate an executable due to --disable-main option enabled.
macro(COMPILE)
    set(options FAIL)
    set(oneValueArgs NAME IMPORT_PATH)
    set(multiValueArgs LABELS EXTRAFILES)
    cmake_parse_arguments(COMPILE "${options}" "${oneValueArgs}"
                          "${multiValueArgs}" ${ARGN} )
    set(name ${COMPILE_NAME})
    if (NOT name)
        message(FATAL_ERROR "Must specify the NAME argument")
    endif()

    set(extra_args "")
    if (COMPILE_IMPORT_PATH)
        # Only one import path supported for now
        # Later add support for multiple import paths by looping over and appending to extra args
        set(extra_args ${extra_args} -I${CMAKE_CURRENT_SOURCE_DIR}/${COMPILE_IMPORT_PATH})
    endif()

    if (${KIND} IN_LIST COMPILE_LABELS)
        if (KIND STREQUAL "llvm")
            add_custom_command(
                OUTPUT ${name}.o
                COMMAND ${LPYTHON} ${extra_args} --disable-main -c ${CMAKE_CURRENT_SOURCE_DIR}/${name}.py -o ${name}.o
                DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/${name}.py
                VERBATIM)
            add_library(${name} OBJECT ${name}.o)
            set_target_properties(${name} PROPERTIES LINKER_LANGUAGE C)
        elseif(KIND STREQUAL "c")
            add_custom_command(
                OUTPUT ${name}.c
                COMMAND ${LPYTHON} ${extra_args} --disable-main --show-c ${CMAKE_CURRENT_SOURCE_DIR}/${name}.py > ${name}.c
                DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/${name}.py
                VERBATIM)
            add_library(${name} OBJECT ${name}.c)
            set_target_properties(${name} PROPERTIES LINKER_LANGUAGE C)
            target_link_libraries(${name} lpython_rtlib)
        elseif(KIND STREQUAL "cpython")
            # CPython test
            set(PY_MOD "")

            add_test(${name} python ${CMAKE_CURRENT_SOURCE_DIR}/${name}.py)
            set_tests_properties(${name} PROPERTIES
                ENVIRONMENT "PYTHONPATH=${CMAKE_SOURCE_DIR}/../src/runtime/lpython:${CMAKE_SOURCE_DIR}/..;LPYTHON_PY_MOD_NAME=${PY_MOD};LPYTHON_PY_MOD_PATH=${CMAKE_CURRENT_BINARY_DIR}")
            if (RUN_LABELS)
                set_tests_properties(${name} PROPERTIES LABELS "${RUN_LABELS}")
            endif()
            if (${RUN_FAIL})
                set_tests_properties(${name} PROPERTIES WILL_FAIL TRUE)
            endif()
        endif()
    endif()
endmacro(COMPILE)


RUN(NAME test_str_01         LABELS cpython llvm)
