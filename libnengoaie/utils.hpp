#ifndef UTILS_HPP
#define UTILS_HPP

#include <boost/program_options.hpp>
#include <vector>
#include <string>
#include <cfloat>

// Include XRT libraries (used in the functions)
#include "xrt/xrt_bo.h"
#include "xrt/xrt_device.h"
#include "xrt/xrt_kernel.h"

namespace utils {

// Check that the file (specified by the option) exists
void check_arg_file_exists(boost::program_options::variables_map &vm_in, std::string name);

// Adds default options to the command line options
void add_default_options(boost::program_options::options_description &desc);

// Parses the arguments based on desc and stores the result in vm
void parse_options(int argc, const char *argv[],
                   boost::program_options::options_description &desc,
                   boost::program_options::variables_map &vm);

// Loads the instruction sequence (in hexadecimal text format) from a file
std::vector<uint32_t> load_instr_sequence(std::string instr_path);

// Loads the binary instruction file
std::vector<uint32_t> load_instr_binary(std::string instr_path);

// Initializes the XRT context and loads the specified kernel
void init_xrt_load_kernel(xrt::device &device, xrt::kernel &kernel,
                          int verbosity, std::string xclbinFileName,
                          std::string kernelNameInXclbin);

// Compares two floats with an epsilon tolerance (utility function for tests)
bool nearly_equal(float a, float b, float epsilon = 128 * FLT_EPSILON,
                  float abs_th = FLT_MIN);

// Writes the trace buffer content to a file
void write_out_trace(char *traceOutPtr, size_t trace_size, std::string path);

} // namespace utils

#endif // UTILS_HPP