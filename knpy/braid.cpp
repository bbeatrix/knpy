#include <stdexcept>
#include <string>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <algorithm>
#include <utility>

namespace py = pybind11;
using array = py::array_t<long long>;

struct IllegalTransformationException : public std::runtime_error {
    using std::runtime_error::runtime_error;
};

int sign_of_non_zero(int x) {
    return x > 0 ? 1 : -1;
}

array shift_left(const array _inp, const int amount = 1) {
    const auto inp = _inp.unchecked<1>();
    const int n = inp.size();
    array _res(n);
    auto res = _res.mutable_unchecked<1>();
    for (int i = 0; i < n; i++) {
        res[i] = inp[(i+amount)%n];
    }
    return _res;
}

array shift_right(const array _inp, const int amount = 1) {
    const auto inp = _inp.unchecked<1>();
    const int n = inp.size();
    array _res(n);
    auto res = _res.mutable_unchecked<1>();
    for (int i = 0; i < n; i++) {
        res[i] = inp[(i-amount+n)%n];
    }
    return _res;
}

bool is_braid_relation1_performable(const array _inp, const int index) {
    const auto inp = _inp.unchecked<1>();
    const int n = inp.size();
    if (inp.size() < 3) return false;
    const int a = inp[(index+0)%n];
    const int b = inp[(index+1)%n];
    const int c = inp[(index+2)%n];

    return abs(a) == abs(c) && abs(abs(b) - abs(a)) == 1 
        && !(sign_of_non_zero(b) != sign_of_non_zero(a) && sign_of_non_zero(b) != sign_of_non_zero(c));
}

array braid_relation1_performable_indices(const array _inp) {
    const auto inp = _inp.unchecked<1>();
    const int n = inp.size();
    array _res(n);
    auto res = _res.mutable_unchecked<1>();
    for (int i = 0; i < n; i++) res[i] = is_braid_relation1_performable(_inp, i);
    return _res;
}

array braid_relation1(const array _inp, const int index) {
    const auto inp = _inp.unchecked<1>();
    const int n = inp.size();

    if (!is_braid_relation1_performable(_inp, index)) {
        throw IllegalTransformationException("Braid relation 1 is not performable at index " + std::to_string(index));
    }

    int signs[3] = {1, 1, 1};
    array _res(n);
    auto res = _res.mutable_unchecked<1>();
    for (int i = 0; i < n; i++) res[i] = inp[i];
    for (int i = 0; i < 3; i++) {
        if (inp[(index+i)%n] < 0) signs[i] = -1;
    }
    for (int i = 0; i < 3; i++) {
        const int j = (index+(i!=1))%n;
        res[(index+i)%n] = signs[2-i] * abs(inp[j]); 
    }
    return _res;
}

bool is_braid_relation2_performable(const array _inp, const int index) {
    const auto inp = _inp.unchecked<1>();
    const int n = inp.size();
    return n != 0 && abs(abs(inp[index]) - abs(inp[(index+1)%n])) >= 2;
}

array braid_relation2_performable_indices(const array _inp) {
    const auto inp = _inp.unchecked<1>();
    const int n = inp.size();
    array _res(n);
    auto res = _res.mutable_unchecked<1>();
    for (int i = 0; i < n; i++) res[i] = is_braid_relation2_performable(_inp, i);
    return _res;
}

array braid_relation2(const array _inp, const int index) {
    const auto inp = _inp.unchecked<1>();
    const int n = inp.size();
    
    if (!is_braid_relation2_performable(_inp, index)) {
        throw IllegalTransformationException("Braid relation 2 is not performable at index " + std::to_string(index));
    }

    array _res(n);
    auto res = _res.mutable_unchecked<1>();
    for (int i = 0; i < n; i++) res[i] = inp[i];
    std::swap(res[index], res[(index+1)%n]);
    return _res;
}

array conjugation(const array _inp, const int value, const int index) {
    const auto inp = _inp.unchecked<1>();
    const int n = inp.size();
    array _res(n+2);
    auto res = _res.mutable_unchecked<1>();
    if (index == n + 1) {
        res[0] = -value;
        res[n+1] = value;
        for (int i = 0; i < n; i++) {
            res[i+1] = inp[i];
        }
    } else {
        res[index] = value;
        res[index+1] = -value;
        for (int i = 0; i < n; i++) {
            res[i + 2*(i>=index)] = inp[i];
        }
    }
    return _res;
}

array stabilization(const array _inp, const int index, const bool on_top, const bool inverse, const int strand_count) {
    const auto inp = _inp.unchecked<1>();
    const int n = inp.size();

    array _res(n+1);
    auto res = _res.mutable_unchecked<1>();
    int new_sigma = inverse ? -1 : 1;
    if (on_top) {
        res[index] = new_sigma;
        for (int i = 0; i < n; i++) {
            res[i+(i>=index)] = inp[i] + sign_of_non_zero(inp[i]);
        }
    } else {
        new_sigma *= strand_count;
        res[index] = new_sigma;
        for (int i = 0; i < n; i++) {
            res[i+(i>=index)] = inp[i];
        }
    }
    return _res;
}

bool is_destabilization_performable(const array _inp, const int index, const int strand_count) {
    const auto inp = _inp.unchecked<1>();
    const int n = inp.size();
    const bool valid_index = 0 <= index && index < n;
    bool ok_bottom_position = false, ok_bottom_elsewhere = true, ok_top_position = false, ok_top_elsewhere = true;
    for (int i = 0; i < n; i++) {
        if (abs(inp[i]) == strand_count - 1) {
            if (i == index) ok_bottom_position = true;
            else ok_bottom_elsewhere = false;
        }
    }

    for (int i = 0; i < n; i++) {
        if (abs(inp[i]) == 1) {
            if (i == index) ok_top_position = true;
            else ok_top_elsewhere = false;
        }
    }
    return valid_index && ((ok_bottom_position && ok_bottom_elsewhere) || (ok_top_position && ok_top_elsewhere));
}

array destabilization(const array _inp, const int index, const int strand_count) {
    const auto inp = _inp.unchecked<1>();
    const int n = inp.size();

    if (!is_destabilization_performable(_inp, index, strand_count)) {
        throw IllegalTransformationException("Destabilization is not performable at index " + std::to_string(index));
    }

    const bool on_top = abs(inp[index]) == 1;
    array _res(n-1);
    auto res = _res.mutable_unchecked<1>();
    for (int i = 0; i<n-1; i++) {
        const int j = i+(i>=index);
        res[i] = inp[j] - on_top * sign_of_non_zero(inp[j]);
    }
    return _res;
}

bool is_remove_sigma_inverse_pair_performable(const array _inp, const int index) {
    const auto inp = _inp.unchecked<1>();
    const int n = inp.size();
    if (n == 0) return false;
    const int j = (index+1)%n;
    return 0 <= index && index < n && inp[index] == -inp[j];
}

array remove_sigma_inverse_pair_performable_indices(const array _inp) {
    const auto inp = _inp.unchecked<1>();
    const int n = inp.size();
    array _res(n);
    auto res = _res.mutable_unchecked<1>();
    for (int i = 0; i < n; i++) res[i] = is_remove_sigma_inverse_pair_performable(_inp, i);
    return _res;
}

array remove_sigma_inverse_pair(const array _inp, const int index) {
    const auto inp = _inp.unchecked<1>();
    const int n = inp.size();

    if (!is_remove_sigma_inverse_pair_performable(_inp, index)) {
        throw IllegalTransformationException("Sigma inverse pair is not removable at index " + std::to_string(index));
    }

    array _res(n-2);
    auto res = _res.mutable_unchecked<1>();
    int cnt = 0;
    for (int i = 0; i < n; i++) {
        if (i != index && i != (index+1)%n) {
            res[cnt++] = inp[i];
        }
    }
    return _res;
}


PYBIND11_MODULE(braid_cpp_impl, m) {
    m.doc() = "Braid C++ implementation";
    py::register_exception<IllegalTransformationException>(m, "IllegalTransformationException");

    // Note that the third parameter of m.def is implicit
    m.def("shift_left", &shift_left, "Shift left implementation");
    m.def("shift_right", &shift_right, "Shift right implementation");
    m.def("is_braid_relation1_performable", &is_braid_relation1_performable, "Is braid relation #1 performable implementation");
    m.def("braid_relation1_performable_indices", &braid_relation1_performable_indices, "Braid relation #1 performable indices implementation");
    m.def("braid_relation1", &braid_relation1, "Braid relation #1 implementation");
    m.def("is_braid_relation2_performable", &is_braid_relation2_performable, "Is braid relation #2 performable implementation");
    m.def("braid_relation2_performable_indices", &braid_relation2_performable_indices, "Braid relation #2 performable indices implementation");
    m.def("braid_relation2", &braid_relation2, "Braid relation #2 implementation");
    m.def("conjugation", &conjugation, "Conjugation implementation");
    m.def("stabilization", &stabilization, "Stabilization implementation");
    m.def("is_destabilization_performable", &is_destabilization_performable, "Is destabilization performable");
    m.def("destabilization", &destabilization, "Destabilization implementation");
    m.def("is_remove_sigma_inverse_pair_performable", &is_remove_sigma_inverse_pair_performable, "Is remove sigma inverse pair performable implementation");
    m.def("remove_sigma_inverse_pair_performable_indices", &remove_sigma_inverse_pair_performable_indices, "Remove sigma inverse pair performable indices implementation");
    m.def("remove_sigma_inverse_pair", &remove_sigma_inverse_pair, "Remove sigma inverse pair implementation");
}
