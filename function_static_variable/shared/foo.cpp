#include "foo.h"
#include "mm.h"
#include "string.h"

class Output {
public:
    Output() {
        std::cout << this << ", output construct +++++++++++++++++==" << std::endl;

        data = strdup("xxxxxxxxxxxx");
    }

    ~Output() {
        free(data);
        data = nullptr;
    }

    void bar(const char * msg) {
        std::cout << this << ", this is output:" << msg << ", " << data << std::endl;
    }

    char * data = nullptr;
};

class FooImpl : public CSingleton<FooImpl> {
public:
    FooImpl() {
        output = new Output;
        std::cout << this << ", foo impl costruct, output:" << output << std::endl;
    }

    virtual ~FooImpl() {
        std::cout << this << ", output:" << output <<", foo impl destruct" << std::endl;
        delete output;
        output = nullptr;
        std::cout << this << ", output:" << output <<", foo impl destruct" << std::endl;
    }

    void bar(const char * msg) {
        std::cout << this << ", output:" << output << ", this is FooImpl::bar:" << msg << std::endl;
        output->bar(msg);
    }

private:
    Output * output = nullptr;
};

void CallBar(const char * msg) {
    auto & p = FooImpl::GetInstance();
    std::cout << "foo instance:" << &p << std::endl;
    FooImpl::GetInstance().bar(msg);
}

void CallBar3(const char * msg) {
    std::cout << "callbar3 called," << msg << std::endl;
}
