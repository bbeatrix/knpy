# KNPY
The braid notation of prime knots is from C. Livingston and A. H. Moore, KnotInfo: Table of Knot Invariants, knotinfo.math.indiana.edu, October 21, 2024

## Installation

```
pip install 'knpy @ git+https://github.com/bbeatrix/knpy'
```

## PR Workflow 

Clone the repo:
```
git clone <repository-url>
```
Create a new branch:
```
git checkout -b <your-branch-name>
```
Stage and commit changes:
```
git add .
git commit -m "Your commit message"
```
Push the branch:
```
git push origin <your-branch-name>
```
Create a pull request and wait for review.

## Faster `Braid` implementation

If you want to use the faster `Braid` implementation in `braid_vec.py`, you need 
to compile the C++ modules.

> ⚠️ Warning: although the APIs are very similar, some features, such as negative 
> indexing is not supported in the faster implementations. **Some errors are omitted
> please test using the python implementation.**

First, make sure that you have `pybind11` and CMake and a useable build 
toolchain installed. Then create a build directory:

```bash
mkdir knpy/build
cd knpy/build
```

Generate the build configuration files:

```bash
cmake ..
```

Then build and install (if you are using make):

```bash
make
make install
```

This will (by default) install the module library and its corresponding `.pyi` 
stub in the `knpy` directory, from where the Python modules can import it.

To use the faster implementation, set the `KNPY_FAST_BRAID` environment variable 
to "true", and import normally: `from knpy import Braid`.
