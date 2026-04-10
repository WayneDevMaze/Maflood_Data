# MAflood Project Documentation

## 1. Project Overview and Core Features

MAflood is an improved fuzzing tool based on the AFL (American Fuzzy Lop) framework, focusing on enhancing the performance and efficiency of multi-threaded fuzzing.

### Core Features:

- **Multi-threaded parallel fuzzing**: Supports multiple threads for simultaneous fuzzing, fully utilizing multi-core CPU resources
- **Dual-pruning model**: Optimizes test case generation and selection to reduce redundant tests and improve testing efficiency
- **Parallel synchronization mechanism**: Shares test cases between threads to avoid duplicate work
- **Coverage-guided genetic algorithm**: Uses code coverage to guide test case generation, improving crash discovery rate
- **Multiple testing modes**: Supports source code instrumentation and binary instrumentation (QEMU mode)

### Technical Innovations:

- **Dual-pruning model**: Reduces the generation of invalid test cases through a combination of static and dynamic analysis
- **Optimized thread synchronization**: Reduces inter-thread communication overhead and improves parallel performance
- **Adaptive testing strategy**: Automatically adjusts testing parameters based on target program characteristics

## 2. Environment Dependencies and Version Requirements

### System Requirements:
- Linux operating system (Ubuntu 18.04 or higher recommended)
- At least 4GB memory
- At least 50GB disk space
- Multi-core CPU (4 cores or more recommended)

### Software Dependencies:
- GCC or Clang compiler
- Make build tool
- Python 3.6 or higher (for data visualization)
- matplotlib library (for data visualization)
- pandas library (for data processing)
- gnuplot (optional, for data visualization)

### Compilation Dependencies:
- build-essential
- libtool
- automake
- git
- wget
- curl

## 3. Detailed Compilation Steps

### 3.1 Install Dependencies

```bash
# Ubuntu/Debian systems
sudo apt update
sudo apt install build-essential libtool automake git wget curl python3 python3-pip
sudo pip3 install matplotlib pandas

# Optional: install gnuplot
sudo apt install gnuplot
```

### 3.2 Compile MAflood

1. Clone the MAflood code repository:

```bash
git clone [MAflood code repository address]
cd MAflood
```

2. Compile the AFL toolchain:

```bash
make clean all
```

3. Compile QEMU mode (optional, for binary instrumentation):

```bash
cd qemu_mode
./build_qemu_support.sh
```

## 4. Running Parameter Configuration Instructions

### 4.1 Basic Running Parameters

MAflood's running parameters are compatible with AFL, including:

- `-i <input_dir>`: Input test case directory
- `-o <output_dir>`: Output results directory
- `-m <memory_limit>`: Memory limit (MB)
- `-t <timeout>`: Timeout (milliseconds)
- `-f <input_file>`: Input file path for target program
- `-M <master_name>`: Master instance name (multi-threaded mode)
- `-S <slave_name>`: Slave instance name (multi-threaded mode)

### 4.2 Multi-threaded Running Configuration

```bash
# Start master instance
./afl-fuzz -i input_dir -o output_dir -M master -- ./target_program @@

# Start slave instances (in different terminals)
./afl-fuzz -i input_dir -o output_dir -S slave1 -- ./target_program @@
./afl-fuzz -i input_dir -o output_dir -S slave2 -- ./target_program @@
./afl-fuzz -i input_dir -o output_dir -S slave3 -- ./target_program @@
```

### 4.3 Advanced Configuration

- `-d`: Disable deterministic testing (speed up testing)
- `-n`: Disable mutation scheduler (use fixed mutation strategy)
- `-x <dict_file>`: Use custom dictionary
- `-c <seed>`: Set random seed

## 5. Complete Experimental Reproduction Process

### 5.1 Prepare Test Targets

1. **LAVA-M Test Suite**:

```bash
# Download LAVA-M test suite
git clone https://github.com/panda-re/lava.git
cd lava
./get_and_build.sh
```

2. **ffjpeg**:

```bash
# Download ffjpeg
git clone https://github.com/FFmpeg/ffmpeg.git
cd ffmpeg
./configure
make
```

3. **libpng**:

```bash
# Download libpng
wget https://downloads.sourceforge.net/libpng/libpng-1.6.37.tar.gz
tar -xzf libpng-1.6.37.tar.gz
cd libpng-1.6.37
./configure
make
```

### 5.2 Compile Test Targets (Source Code Instrumentation)

```bash
# Compile with afl-gcc
export CC=/path/to/MAflood/afl-gcc
export CXX=/path/to/MAflood/afl-g++

# Compile LAVA-M targets
cd /path/to/lava/bin
make clean
export CC=/path/to/MAflood/afl-gcc
make

# Compile ffjpeg
cd /path/to/ffmpeg
export CC=/path/to/MAflood/afl-gcc
export CXX=/path/to/MAflood/afl-g++
./configure
make

# Compile libpng
cd /path/to/libpng-1.6.37
export CC=/path/to/MAflood/afl-gcc
export CXX=/path/to/MAflood/afl-g++
./configure
make
```

### 5.3 Run Fuzzing

1. **LAVA-M Test**:

```bash
# Create input directory
mkdir -p input_lava
cp /path/to/lava/inputs/* input_lava/

# Run MAflood (4 threads)
./afl-fuzz -i input_lava -o output_lava -M master -- /path/to/lava/bin/base64 @@
./afl-fuzz -i input_lava -o output_lava -S slave1 -- /path/to/lava/bin/base64 @@
./afl-fuzz -i input_lava -o output_lava -S slave2 -- /path/to/lava/bin/base64 @@
./afl-fuzz -i input_lava -o output_lava -S slave3 -- /path/to/lava/bin/base64 @@
```

2. **ffjpeg Test**:

```bash
# Create input directory
mkdir -p input_ffjpeg
cp /path/to/sample_images/* input_ffjpeg/

# Run MAflood (single thread)
./afl-fuzz -i input_ffjpeg -o output_ffjpeg -- /path/to/ffmpeg/ffmpeg -i @@ -f null -
```

3. **libpng Test**:

```bash
# Create input directory
mkdir -p input_libpng
cp /path/to/sample_pngs/* input_libpng/

# Run MAflood (single thread)
./afl-fuzz -i input_libpng -o output_libpng -- /path/to/libpng-1.6.37/pngtest @@
```

### 5.4 Collect and Analyze Results

```bash
# View crashes and hangs
tree output_dir/crashes/
tree output_dir/hangs/

# Analyze code coverage
./afl-showmap -o coverage.txt -- /path/to/target_program @@

# Generate performance report
python3 /path/to/MAflood/visualization/extract_data.py
```

## 6. Details of Completed Experimental Settings

### 6.1 Experimental Environment

- **Operating System**: Ubuntu 18.04 LTS
- **CPU**: Intel Core i7-8700K (6 cores, 12 threads)
- **Memory**: 16GB DDR4
- **Storage**: 512GB SSD

### 6.2 Test Targets

| Test Target | Version | Type | Test Cases |
|-------------|---------|------|------------|
| LAVA-M | 2017 | Injected vulnerabilities | 100 seed files |
| ffjpeg | 4.2.2 | Image processing | 50 BMP/JPEG samples |
| libpng | 1.6.37 | Image processing | 50 PNG samples |

### 6.3 Experimental Parameter Configuration

| Tool | Threads | Running Time | Memory Limit | Timeout Setting |
|------|---------|--------------|--------------|----------------|
| AFL | 1, 4, 8 | 24 hours | 256MB | 1000ms |
| AFLFast | 1, 4, 8 | 24 hours | 256MB | 1000ms |
| MAflood | 1, 4, 8 | 24 hours | 256MB | 1000ms |

### 6.4 Variable Control

- **Input Seeds**: All tools use the same input seed set
- **Running Time**: All experiments run for the same duration (24 hours)
- **Hardware Resources**: All experiments run in the same hardware environment
- **Compilation Options**: All targets use the same compilation options

## 7. Common Problem Solutions

### 7.1 Compilation Errors

**Problem**: Compiling AFL results in `error: 'for' loop initial declarations are only allowed in C99 mode`

**Solution**: Compile with C99 standard

```bash
export CFLAGS="-std=c99"
make clean all
```

### 7.2 Running Errors

**Problem**: Running results in `[*] Hmm, your system is configured to send core dump notifications to an external utility. This will cause issues: there's a small window of time between receiving a SIGSEGV and the core dump handler firing, where afl-fuzz might not be able to reset the target process.`

**Solution**: Disable core dump notifications

```bash
echo core > /proc/sys/kernel/core_pattern
```

### 7.3 Performance Issues

**Problem**: Fuzzing speed is slow

**Solution**:
- Increase the number of threads
- Adjust memory limit
- Use `-d` parameter to disable deterministic testing
- Ensure target program is compiled with optimizations

### 7.4 Coverage Issues

**Problem**: Code coverage grows slowly

**Solution**:
- Use a larger seed set
- Add custom dictionary (`-x` parameter)
- Adjust mutation strategy
- Check if the target program has complex input validation

## 8. Experimental Result Visualization

### 8.1 Visualization Tools

- **Python + Matplotlib**: For generating detailed performance charts
- **Gnuplot**: For generating real-time performance monitoring charts

### 8.2 Generate Visualization Charts

```bash
# Enter visualization directory
cd /path/to/MAflood/visualization

# Run data extraction and visualization script
python3 extract_data.py

# View generated charts
ls -la *.png
```

### 8.3 Chart Descriptions

Generated charts include:

- **Crash Discovery Rate Comparison**: Shows the crash discovery speed under different tools and thread configurations
- **Code Coverage Comparison**: Shows the code coverage growth under different tools and thread configurations
- **Execution Speed Comparison**: Shows the average execution speed under different tools and thread configurations
- **Test Case Count Comparison**: Shows the test case generation count under different tools and thread configurations

## 9. Project Structure

```
MAflood/
├── afl-fuzz.c          # Core fuzzing code
├── afl-gcc.c           # GCC instrumentation tool
├── afl-clang.c         # Clang instrumentation tool
├── qemu_mode/          # QEMU mode support
├── docs/               # Documentation
├── experiment/         # Experimental data
│   ├── LAVA-M/         # LAVA-M test results
│   ├── ffjpeg/         # ffjpeg test results
│   └── libpng/         # libpng test results
└── visualization/      # Data visualization tools
    ├── extract_data.py # Data extraction script
    └── *.png           # Generated charts
```

## 10. Conclusion

MAflood significantly improves the performance and efficiency of multi-threaded fuzzing by introducing a dual-pruning model and optimized thread synchronization mechanism. Experimental results show that MAflood outperforms traditional AFL and AFLFast tools in terms of crash discovery rate, code coverage, and execution speed.

### Key Improvements:

1. **Dual-pruning model**: Reduces redundant test cases and improves testing efficiency
2. **Optimized thread synchronization**: Reduces inter-thread communication overhead and improves parallel performance
3. **Adaptive testing strategy**: Automatically adjusts testing parameters based on target program characteristics

MAflood provides an efficient multi-threaded solution for the field of fuzzing, especially suitable for security testing of large and complex programs.

## 11. References

1. American Fuzzy Lop (AFL): https://lcamtuf.coredump.cx/afl/
2. AFLFast: https://github.com/mboehme/aflfast
3. LAVA-M: https://github.com/panda-re/lava
4. libpng: https://libpng.sourceforge.io/
5. FFmpeg: https://ffmpeg.org/
