#include <stdexcept>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <algorithm>
#include <utility>

namespace py = pybind11;
using array = py::array_t<long long>;

struct IllegalTransformationException : public std::runtime_error {};

int strand_count(array _inp) {
    auto inp = _inp.unchecked<1>();
    long long mx = 0;
    for (int i = 0; i < inp.size(); i++) {
        mx = std::max(mx, inp[i]);
    }
    return mx + 1;
}

int sign(int x) {
    return x > 0 ? 1 : -1;
}

array shift_left(array _inp, int amount = 1) {
    auto inp = _inp.unchecked<1>();
    int n = inp.size();
    array _res(n);
    auto res = _res.mutable_unchecked();
    for (int i = 0; i < n; i++) {
        res[i] = inp[(i+amount)%n];
    }
    return _res;
}

array shift_right(array _inp, int amount = 1) {
    auto inp = _inp.unchecked<1>();
    int n = inp.size();
    array _res(n);
    auto res = _res.mutable_unchecked();
    for (int i = 0; i < n; i++) {
        res[i] = inp[(i-amount+n)%n];
    }
    return _res;
}

bool is_braid_relation1_performable(array _inp, int index) {
    auto inp = _inp.unchecked<1>();
    int n = inp.size();
    if (inp.size() < 3) return false;
    int a = inp[(index+0)%n];
    int b = inp[(index+1)%n];
    int c = inp[(index+2)%n];

    return abs(a) == abs(c) && abs(abs(b) - abs(a)) == 1 
        && !(sign(b) != sign(a) && sign(b) != sign(c));
}

array braid_relation1(array _inp, int index) {
    auto inp = _inp.unchecked<1>();
    int n = inp.size();
    if (is_braid_relation1_performable(_inp, index)) {
        int signs[3] = {0, 0, 0};
        array _res(n);
        auto res = _res.mutable_unchecked();
        for (int i = 0; i < n; i++) res[i] = inp[i];
        for (int i = 0; i < 3; i++) {
            // TODO % optimisation
            if (inp[(index+i)%n] < 0) signs[i] = -1;
        }
        for (int i = 0; i < 3; i++) {
            int j = (index+i+(i!=1))%n;
            res[(index+i)%n] = signs[2-i] * abs(inp[j]); 
        }
        return _res;
    } else {
        throw 1;
    }
}

bool is_braid_relation2_performable(array _inp, int index) {
    auto inp = _inp.unchecked<1>();
    int n = inp.size();
    int i = (index+1)%n;
    return n != 0 && abs(abs(inp[index]) - abs(inp[i])) >= 2;
}

array braid_relation2(array _inp, int index) {
    auto inp = _inp.unchecked<1>();
    int n = inp.size();
    if (is_braid_relation2_performable(_inp, index)) {
        array _res(n);
        auto res = _res.mutable_unchecked();
        for (int i = 0; i < n; i++) res[i] = inp[i];
        std::swap(res[index], res[(index+1)%n]);
        return _res;
    } else {
        throw 1;
    }
}

bool is_conjugation_performable(array _inp, int value, int index) {
    return true;
}

array conjugation(array _inp, int value, int index) {
    auto inp = _inp.unchecked<1>();
    int n = inp.size();
    if (is_conjugation_performable(_inp, value, index)) {
        array _res(n+2);
        auto res = _res.mutable_unchecked();
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
        return _res;
    } else {
        throw 1;
    }
}

array stabilization(array _inp, int index, bool on_top = false, bool inverse = false) {
    auto inp = _inp.unchecked<1>();
    int n = inp.size();

    array _res(n+1);
    auto res = _res.mutable_unchecked();
    int new_sigma = inverse ? -1 : 1;
    if (on_top) {
        res[index] = new_sigma;
        for (int i = 0; i < n; i++) {
            res[i+(i>=index)] = inp[i] + sign(inp[i]);
        }
    } else {
        new_sigma *= strand_count(_inp);
        res[index] = new_sigma;
        for (int i = 0; i < n; i++) {
            res[i+(i>=index)] = inp[i];
        }
    }
    return _res;
}

bool is_destabilization_performable(array _inp, int index) {
    auto inp = _inp.unchecked<1>();
    int n = inp.size();
    bool valid_index = 0 <= index < n;
    bool ok1 = false, ok2 = true, ok3 = false, ok4 = true;
    int cnt = strand_count(_inp) - 1;
    for (int i = 0; i < n; i++) {
        if (abs(inp[i]) == cnt) {
            if (i == index) ok1 = true;
            else ok2 = false;
        }
    }
    for (int i = 0; i < n; i++) {
        if (abs(inp[i]) == 1) {
            if (i == index) ok3 = true;
            else ok4 = false;
        }
    }
    return valid_index && ((ok1 && ok2) || (ok3 && ok4));
}

array destabilization(array _inp, int index) {
    auto inp = _inp.unchecked<1>();
    int n = inp.size();
    if (is_destabilization_performable(_inp, index)) {
        bool on_top = abs(inp[index]) == 1;
        array _res(n-1);
        auto res = _res.mutable_unchecked();
        for (int i = 0; i<n-1; i++) {
            int j = i+(i>=index);
            res[i] = inp[j] - on_top * (sign(inp[j]));
        }
        return _res;
    } else {
        throw 1;
    }
}

bool is_remove_sigma_inverse_pair_performable(array _inp, int index) {
    auto inp = _inp.unchecked<1>();
    int n = inp.size();
    int j = (index+1)%n;
    return n != 0 && inp[index] == -inp[j];
}

array remove_sigma_inverse_pair(array _inp, int index) {
    auto inp = _inp.unchecked<1>();
    int n = inp.size();
    if (is_remove_sigma_inverse_pair_performable(_inp, index)) {
        array _res(n-2);
        auto res = _res.mutable_unchecked();
        for (int i = 0; i < n-2; i++) {
            res[i] = inp[i + 2 * (i>=index)];
        }
        return _res;
    } else {
        throw 1;
    }
}


PYBIND11_MODULE(braid_cpp_impl, m) {
    m.doc() = "Braid C++ implementation";
    py::register_exception<IllegalTransformationException>(
        m, "IllegalTransformationException");

    m.def("shift_left", &shift_left, "Shift left implementation");
}
