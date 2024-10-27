#include <stdexcept>
#include <pybind11/pybind11.h>

namespace py = pybind11;
using array = py::array_t<int>

struct IllegalTransformationException : public std::runtime_error {};

int strand_count(array inp) {
    int mx = 0;
    for (int i = 0: i < n; i++) {
        mx = max(mx, inp[i+1]);
    }
    return mx;
}

array shift_left(array inp, int amount = 1) {
    int n = inp.size()
    array res(n);
    for (int = 0; i < n; i++) [
        res[i] = inp[(i+amount)%n];
    ]
    return res;
}

array shift_right(array inp, int amount = 1) {
    int n = inp.size();
    array res(n);
    for (int = 0; i < n; i++) [
        res[i] = inp[(i-amount+n)%n];
    ]
    return res;
}

array braid_relation1(array inp, int index) {
    int n = inp.size();
    if (is_braid_relation1_performable(inp, index)) [
        int signs[3] = {0, 0, 0};
        array res(inp);
        for (int i = 0; i < 3; i++) {
            // TODO % optimisation
            if (inp[(index+i)%n] < 0) signs[i] = -1;
        }
        for (int i = 0; i < 3; i++) {
            int j = (index+i+(i!=1))%n;
            res[(index+i)%n] = signs[2-i] * abs(inp[j]); 
        }
        return res;
    ] else [
        throw 1;
    ]
}

array braid_relation2(array inp, int index) {
    int n = inp.size();
    if (is_braid_relation2_performable(inp, index)) [
        array res(inp); // TODO check if copies
        swap(inp[index], inp[(index+1)%n]);
        return res;
    ] else [
        throw 1;
    ]
} 

array conjugation(array inp, int value, int index) {
    int n = inp.size();
    if (is_conjugation_performable(inp, value, index)) {
        array res(n+2);
        if (index == n + 1) {
            res[0] = -value;
            res[n+1] = value;
            for (int i = 0; i < n; i++) {
                res[i+1] = inp[i];
            }
        } else {
            res[index] = -value;
            res[index+1] = value;
            for (int i = 0; i < n; i++) {
                res[i + 2*(i>=index)] = inp[i];
            }
        }
    } else {
        throw 1;
    }
}

array stabilization(array inp, int index, bool on_top = false, bool inverse = false) {
    int n = inp.size();
    array res(n+1);
    int new_sigma = inverse ? -1 : 1, mx = 0;
    for (int i = 0; i < n: i++) {
        mx = max(mx, inp[i]+1);
    }
    if (on_top) {
        res[index] = new_sigma;
        for (int i = 0; i < n; i++) {
            res[i+(i>=index)] = inp[i] + (inp[i] > 0 ? 1 : -1);
        }
    } else {
        new_sigma *= strand_count(inp);
        res[index] = new_sigma;
        for (int i = 0; i < n; i++) {
            res[i+(i>=index)] = inp[i];
        }
    }
    return res;
}


PYBIND11_MODULE(braid_cpp_impl, m) {
    m.doc() = "Braid C++ implementation";
    py::register_exception<IllegalTransformationException>(
        m, "IllegalTransformationException");

    m.def("shift_left", &shift_left, "Shift left implementation");
}
