#include "foo.h"
#include <iostream>
#include <dlfcn.h>

void call_lib(const char * lib_path, const char * msg, bool unload = true, const char * func_name = "CallBar") {
    void * handle = dlopen(lib_path, RTLD_NOW | RTLD_LOCAL);

    if (!handle) {
        std::cerr << "unable to load:" << lib_path
                  << ", error:" << dlerror()
                  << std::endl;
        exit(2);
    }

    std::cout << "lib handle:" << handle << std::endl;

    CALL_BAR func = (CALL_BAR)dlsym(handle, func_name);

    if (!func) {
        std::cerr << "unable to find CallBar func"
                  << ", error:" << dlerror()
                  << std::endl;
        dlclose(handle);

        exit(3);
    }

    std::cout << "callbar func:" << func_name << ", " << (void *)func << std::endl;

    func(msg);

    // MyClass::GetInstance()->MyFunc(msg);

    if (unload)
        dlclose(handle);

    // MyClass::GetInstance()->MyFunc(msg);
}

int main(int argc, char ** argv) {
    if (argc < 3) {
        std::cerr << "Usage: prog <foo.so> <foo_different_path.so>" << std::endl;
        exit(1);
    }

    std::cout << std::endl << "run first round, call CallBar3 which do not trigger Singleton construct" << std::endl;

    call_lib(argv[1], "first round", true, "CallBar3");

    std::cout << std::endl << "run second round, call CallBar trigger singleton construct, but dlclose will destruct the singleton" << std::endl;

    call_lib(argv[2], "second round", true, "CallBar");

    std::cout << std::endl << "run third round" << std::endl;

    call_lib(argv[2], "third round", true, "CallBar");
    return 0;
}
