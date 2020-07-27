#pragma once

extern "C"
{
    void CallBar(const char * msg);
    typedef void (*CALL_BAR)(const char *msg);
    void CallBar3(const char * msg);
    typedef void (*CALL_BAR3)(const char *msg);
}

#include <iostream>
#include <memory>

template<class T>
class Bar {
public:
    virtual ~Bar() {
        std::cout << "bar instance desstruct:" << this << ", " << m_FooPtr.get() << std::endl;
    }

    Bar(T * p) : m_FooPtr{p}
    {
        GetInstance() = m_FooPtr.get();
        std::cout << "bar instance construct:" << this << ", " << p << std::endl;
    }

    std::unique_ptr<T> m_FooPtr;

    T * & GetInstance() {
        static T * instance = NULL;

        return instance;
    }
};

template<class T>
class Foo {
public:
    Foo() {
        std::cout << "foo instance construct:" << this << std::endl;
    }

    virtual ~Foo() {
        std::cout << "foo instance destruct:" << this << std::endl;
    }

public:
    void bar(const char * msg) {
        std::cout << "this is bar:" << msg << std::endl;
    }

    static T * GetInstance() {
        static Bar<T> instance{new T};

        return instance.GetInstance();
    }

};
