cmake_minimum_required(VERSION 3.5)

# Moving files to binary dir to create python package
foreach(py_file "setup.py" "src/ecole/__init__.py")
	configure_file(
		"${CMAKE_CURRENT_SOURCE_DIR}/${py_file}.in" "${CMAKE_CURRENT_BINARY_DIR}/${py_file}"
		@ONLY
	)
endforeach(py_file)


# Temporary override pybind11 version to 2.5 otherwise pinned down by xtensor-python
# Until https://github.com/conda-forge/xtensor-python-feedstock/pull/65 is merged
include(FetchContent)
FetchContent_Declare(
	PyBind11
	URL https://github.com/pybind/pybind11/archive/v2.6.0.tar.gz
	URL_HASH SHA256=90b705137b69ee3b5fc655eaca66d0dc9862ea1759226f7ccd3098425ae69571
)
set(PYBIND11_CPP_STANDARD -std=c++17)
FetchContent_MakeAvailable(PyBind11)
# find_package(pybind11 REQUIRED)
find_package(xtensor REQUIRED)
find_package(xtensor-python REQUIRED)

pybind11_add_module(
	ecole-python SYSTEM
	src/ecole/core/core.cpp
	src/ecole/core/scip.cpp
	src/ecole/core/data.cpp
	src/ecole/core/observation.cpp
	src/ecole/core/reward.cpp
	src/ecole/core/information.cpp
	src/ecole/core/dynamics.cpp
)

target_include_directories(ecole-python PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src/ecole/core)

# Include the headers directly instead of using the CMake target due to it wrongly linking against
# libpython
target_include_directories(ecole-python SYSTEM PRIVATE "${NUMPY_INCLUDE_DIRS}")

target_link_libraries(
	ecole-python
	PRIVATE
		Ecole::libecole
		Ecole::warnings
		xtensor
		xtensor-python
)
if(CMAKE_BUILD_TYPE MATCHES Release)
	target_link_libraries(ecole-python PRIVATE xtensor::optimize)
endif()

set_target_properties(
	ecole-python PROPERTIES
	OUTPUT_NAME core
)
# If no output directory specified, preserve the src/ecole layout
if(DEFINED CMAKE_LIBRARY_OUTPUT_DIRECTORY)
	set_target_properties(
		ecole-python PROPERTIES
		LIBRARY_OUTPUT_DIRECTORY "${CMAKE_LIBRARY_OUTPUT_DIRECTORY}"
	)
else()
	set_target_properties(
		ecole-python PROPERTIES
		LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/src/ecole"
	)
endif()


set(
	PYTHON_FILES
	"py.typed" "typing.py" "version.py"
	"data.py" "observation.py" "reward.py" "information.py" "scip.py" "environment.py"
	"_set_cover_generator.py"
	"_combinatorial_auction_generator.py"
	"_capacitated_facility_location_generator.py"
	"_independent_set_generator.py"
	"instance.py"
)
set(PYTHON_SOURCE_FILES ${PYTHON_FILES})
list(TRANSFORM PYTHON_SOURCE_FILES PREPEND "${CMAKE_CURRENT_SOURCE_DIR}/src/ecole/")
set(PYTHON_COPIED_FILES ${PYTHON_FILES})
list(TRANSFORM PYTHON_COPIED_FILES PREPEND "${CMAKE_CURRENT_BINARY_DIR}/src/ecole/")

add_custom_target(
	ecole-python-files
	COMMAND ${CMAKE_COMMAND} -E copy_if_different ${PYTHON_SOURCE_FILES} "${CMAKE_CURRENT_BINARY_DIR}/src/ecole"
	COMMENT "Copying Python files"
)
add_dependencies(ecole-python ecole-python-files)

if(ENABLE_PYTHON_VENV)
	add_custom_command(
		OUTPUT "${CMAKE_BINARY_DIR}/venv"
		DEPENDS ecole-python ecole-python-files
		COMMAND venv-python -m pip install --upgrade ${CMAKE_CURRENT_BINARY_DIR} > /dev/null
		COMMENT "Installing ecole in virtual environment"
	)

	add_custom_target(ecole-venv ALL DEPENDS "${CMAKE_BINARY_DIR}/venv")
endif()

# Add test if this is the main project and testing is enabled
if(CMAKE_PROJECT_NAME STREQUAL PROJECT_NAME AND BUILD_TESTING)
	add_subdirectory(tests)
endif()
