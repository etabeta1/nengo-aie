#include "utils.hpp"

#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <stdexcept>
#include <cstdlib>
#include <ctime>
#include <cstring>
#include <cassert>
#include <cmath>
#include <limits>
#include <chrono>
#include <algorithm>
#include <cfloat>

namespace po = boost::program_options;

namespace utils {

/**
 * @brief Checks whether a file associated with the given argument exists.
 *
 * This function looks up the file name from the boost::program_options
 * variables map using the provided key and then tests if the file can be opened.
 * If the key is not present or the file cannot be opened, it throws an error.
 *
 * @param vm_in The boost::program_options variables map.
 * @param name The key name corresponding to the file.
 *
 * @throws std::runtime_error if the file is not provided or does not exist.
 */
void check_arg_file_exists(po::variables_map &vm_in, std::string name) {
  if (!vm_in.count(name)) {
    throw std::runtime_error("Error: no " + name + " file was provided\n");
  } else {
    std::ifstream test(vm_in[name].as<std::string>());
    if (!test) {
      throw std::runtime_error("The " + name + " file " +
                               vm_in[name].as<std::string>() +
                               " does not exist.\n");
    }
  }
}

/**
 * @brief Adds default command-line options to the options description.
 *
 * This function defines and adds a set of default options such as help,
 * xclbin path, kernel name, verbosity, instruction file path, verification flag,
 * iteration counts, warmup, trace size, and trace file path to the provided options description.
 *
 * @param desc The boost::program_options options_description object to which the options are added.
 */
void add_default_options(po::options_description &desc) {
  desc.add_options()
      ("help,h", "produce help message")
      ("xclbin,x", po::value<std::string>()->required(), "the input xclbin path")
      ("kernel,k", po::value<std::string>()->required(), "the kernel name in the XCLBIN (for instance PP_PRE_FD)")
      ("verbosity,v", po::value<int>()->default_value(0), "the verbosity of the output")
      ("instr,i", po::value<std::string>()->required(), "path of file containing userspace instructions sent to the NPU")
      ("verify", po::value<bool>()->default_value(true), "whether to verify the AIE computed output")
      ("iters", po::value<int>()->default_value(1))
      ("warmup", po::value<int>()->default_value(0))
      ("trace_sz,t", po::value<int>()->default_value(0))
      ("trace_file", po::value<std::string>()->default_value("trace.txt"), "where to store trace output");
}

/**
 * @brief Parses and validates command-line options.
 *
 * This function uses boost::program_options to parse the command-line arguments.
 * It stores the parsed options in a variables map, handles the display of the help message,
 * and verifies that required files (xclbin and instruction file) exist.
 *
 * @param argc The number of command-line arguments.
 * @param argv The array of command-line argument strings.
 * @param desc The boost::program_options options_description object defining accepted options.
 * @param vm The variables map where the parsed options will be stored.
 */
void parse_options(int argc, const char *argv[],
                   po::options_description &desc,
                   po::variables_map &vm) {
  try {
    po::store(po::parse_command_line(argc, argv, desc), vm);
    po::notify(vm);
    if (vm.count("help")) {
      std::cout << desc << "\n";
      std::exit(1);
    }
  } catch (const std::exception &ex) {
    std::cerr << ex.what() << "\n\n";
    std::cerr << "Usage:\n" << desc << "\n";
    std::exit(1);
  }

  try {
    check_arg_file_exists(vm, "xclbin");
    check_arg_file_exists(vm, "instr");
  } catch (const std::exception &ex) {
    std::cerr << ex.what() << "\n\n";
  }
}

/**
 * @brief Loads a sequence of instructions from a text file.
 *
 * This function opens the instruction file specified by the path, reads each line,
 * converts the hexadecimal value on that line into a uint32_t, and appends it to a vector.
 *
 * @param instr_path The file path to the instruction file.
 * @return A vector of uint32_t containing the instruction sequence.
 *
 * @throws std::runtime_error if any line in the file cannot be parsed.
 */
std::vector<uint32_t> load_instr_sequence(std::string instr_path) {
  std::ifstream instr_file(instr_path);
  std::string line;
  std::vector<uint32_t> instr_v;
  while (std::getline(instr_file, line)) {
    std::istringstream iss(line);
    uint32_t a;
    if (!(iss >> std::hex >> a)) {
      throw std::runtime_error("Unable to parse instruction file\n");
    }
    instr_v.push_back(a);
  }
  return instr_v;
}

/**
 * @brief Loads instructions from a binary file.
 *
 * This function opens the binary instruction file, checks that the file size is a multiple of 4 bytes,
 * reads the entire file into a vector of uint32_t, and returns the vector.
 *
 * @param instr_path The file path to the binary instruction file.
 * @return A vector of uint32_t containing the instructions.
 *
 * @throws std::runtime_error if the file cannot be opened, its size is not valid, or reading fails.
 */
std::vector<uint32_t> load_instr_binary(std::string instr_path) {
  std::ifstream instr_file(instr_path, std::ios::binary);
  if (!instr_file.is_open()) {
    throw std::runtime_error("Unable to open instruction file\n");
  }
  instr_file.seekg(0, std::ios::end);
  std::streamsize size = instr_file.tellg();
  instr_file.seekg(0, std::ios::beg);
  if (size % 4 != 0) {
    throw std::runtime_error("File size is not a multiple of 4 bytes\n");
  }
  std::vector<uint32_t> instr_v(size / 4);
  if (!instr_file.read(reinterpret_cast<char *>(instr_v.data()), size)) {
    throw std::runtime_error("Failed to read instruction file\n");
  }
  return instr_v;
}

/**
 * @brief Initializes the XRT device and loads the specified kernel.
 *
 * This function creates an XRT device with a preset index, loads the xclbin file,
 * searches for the kernel that has a name starting with the specified kernel name,
 * registers the xclbin with the device, and then retrieves the hardware context and kernel handle.
 * Debug messages are printed if the verbosity level is set high.
 *
 * @param device Reference to the XRT device to be initialized.
 * @param kernel Reference to the XRT kernel to be loaded.
 * @param verbosity The verbosity level for logging information.
 * @param xclbinFileName The file path to the xclbin file.
 * @param kernelNameInXclbin The name prefix of the kernel within the xclbin file.
 */
void init_xrt_load_kernel(xrt::device &device, xrt::kernel &kernel,
                          int verbosity, std::string xclbinFileName,
                          std::string kernelNameInXclbin) {
  unsigned int device_index = 0;
  device = xrt::device(device_index);
  if (verbosity >= 1)
    std::cout << "Loading xclbin: " << xclbinFileName << "\n";
  auto xclbin = xrt::xclbin(xclbinFileName);
  if (verbosity >= 1)
    std::cout << "Kernel opcode: " << kernelNameInXclbin << "\n";
  auto xkernels = xclbin.get_kernels();
  auto xkernel =
      *std::find_if(xkernels.begin(), xkernels.end(),
                    [kernelNameInXclbin, verbosity](xrt::xclbin::kernel &k) {
                      auto name = k.get_name();
                      if (verbosity >= 1)
                        std::cout << "Name: " << name << std::endl;
                      return name.rfind(kernelNameInXclbin, 0) == 0;
                    });
  auto kernelName = xkernel.get_name();
  if (verbosity >= 1)
    std::cout << "Registering xclbin: " << xclbinFileName << "\n";
  device.register_xclbin(xclbin);
  if (verbosity >= 1)
    std::cout << "Getting hardware context.\n";
  xrt::hw_context context(device, xclbin.get_uuid());
  if (verbosity >= 1)
    std::cout << "Getting handle to kernel:" << kernelName << "\n";
  kernel = xrt::kernel(context, kernelName);
  return;
}

/**
 * @brief Compares two floating point numbers for near equality.
 *
 * This function checks if two floating point values are nearly equal using a specified relative epsilon
 * and an absolute threshold. It returns true if the values are considered equal within these tolerances.
 *
 * @param a The first floating point number.
 * @param b The second floating point number.
 * @param epsilon The relative tolerance value.
 * @param abs_th The absolute tolerance value.
 * @return true if the two numbers are nearly equal, false otherwise.
 */
bool nearly_equal(float a, float b, float epsilon, float abs_th) {
  assert(std::numeric_limits<float>::epsilon() <= epsilon);
  assert(epsilon < 1.f);
  if (a == b)
    return true;
  auto diff = std::abs(a - b);
  auto norm = std::min((std::abs(a) + std::abs(b)),
                       std::numeric_limits<float>::max());
  return diff < std::max(abs_th, epsilon * norm);
}

/**
 * @brief Writes trace output data to a file.
 *
 * This function writes the data stored at the trace pointer to a file specified by the path.
 * Each 32-bit trace element is output in hexadecimal format with a fixed width of 8 digits.
 *
 * @param traceOutPtr Pointer to the trace output data.
 * @param trace_size The size of the trace data in bytes.
 * @param path The file path where the trace output will be written.
 */
void write_out_trace(char *traceOutPtr, size_t trace_size, std::string path) {
  std::ofstream fout(path);
  uint32_t *traceOut = reinterpret_cast<uint32_t *>(traceOutPtr);
  for (int i = 0; i < trace_size / sizeof(traceOut[0]); i++) {
    fout << std::setfill('0') << std::setw(8) << std::hex << static_cast<int>(traceOut[i]);
    fout << std::endl;
  }
}

} // namespace test_utils