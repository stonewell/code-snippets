#pragma once

#include <list>
#include <assert.h>
#include <memory>

template<class Impl, class T, class TInt>
class CSingletonHelper;

struct CSingletonManager;

template<class Interface>
class ISingleton
{
public:
    static Interface& GetInstance();
};

template<class Impl, class Interface = Impl>
using CSingleton = CSingletonHelper<Impl, Interface, Interface>;

template<class Impl, class Interface>
using CSingletonWithInterface = CSingleton<Impl, Interface>;

template<class Impl, class Interface>
using CPolymorphicSingleton = CSingletonHelper<Impl, Impl, Interface>;

// Base class for all singletons
class IMockableSingletonPtr
{
public:
    virtual void Delete() = 0;
};

// Global singleton manager
struct CSingletonManager
{
    CSingletonManager() {}

    ~CSingletonManager()
    {
    }

    // Helper functions used to leak and unleak singletons
    bool LeakSingleton(bool bSetFlag = false, bool bFlagValue = false) const
    {
        static bool bGlobalLeakSingletonsFlag = false;

        if (bSetFlag)
            bGlobalLeakSingletonsFlag = bFlagValue;

        return bGlobalLeakSingletonsFlag;
    }

    static CSingletonManager& GetInstance()
    {
        // Function local static here used, even on winxp compatible builds
        // Function local statics are safe to use on winxp, as long as they are initialized in a thread-safe manner (and there is no other bug in the compiler).
        // On winxp compatible builds, the client must call INIT_SINGLETON_MANAGER() where statics are initialized so it will be constructed when the module is loaded.
        // Since there is only one thread loading the module, we can safely initialize the singleton manager.
        static CSingletonManager singletonManager;
        return singletonManager;
    }
};

// Used in CMockableSingletonPtr
template<class T, class TInt>
void default_delete(TInt *p) throw()
{
    delete static_cast<T*>(p);
}

// This is where most of the magic happens.
// This class will always hold the singleton instance in a std::unique_ptr.
// However, the singleton instance is accessed by a static pointer which is initially set to the pointer managed by the unique pointer.
// In unit tests, this static pointer can be swapped to point to a mocked implementation of the singleton instance.
// After the unit test, the static pointer should be swapped back to point to the original singleton instance.
template <class T, class TInt = T>
class CMockableSingletonPtr : public IMockableSingletonPtr
{
public:
    // Use template metafunctions to pick the correct constructor at compile time.
    // In this case, the compiler will only use this constructor if Impl inherits from TInt
    template<typename Impl, typename std::enable_if<std::is_base_of<TInt, Impl>::value, int>::type = 0>
    CMockableSingletonPtr(Impl* p) : m_spSingletonPtr(p, default_delete<Impl, TInt>)
    {
        assert(GetRefToSingletonPtr() == NULL);
        GetRefToSingletonPtr() = m_spSingletonPtr.get();
    }

    virtual ~CMockableSingletonPtr()
    {
        if (CSingletonManager::GetInstance().LeakSingleton())
            m_spSingletonPtr.release(); // unique_ptr will "release" the ownership of the pointer.
    }

    // Return reference to the singleton pointer. In production, the pointer value will only change once when the singleton is being initialized.
    // In unit tests, the pointer value will be changed to point to mocked implementations.
    static TInt*& GetRefToSingletonPtr()
    {
        // This function local static is guaranteed to be initialized in a thread safe way in CSingletonHelper::GetInstance()
        static TInt* pSingletonPtr = NULL;
        return pSingletonPtr;
    }

    virtual void Delete()
    {
        GetRefToSingletonPtr() = NULL;
        delete this;
    }

private:
    CMockableSingletonPtr(const CMockableSingletonPtr& rhs); // forbid copy constructor
    CMockableSingletonPtr& operator=(const CMockableSingletonPtr& rhs); // forbid assignment construction

    std::unique_ptr<TInt, void(*)(TInt*)> m_spSingletonPtr;
};

// Templated class for singletons. All types of singletons share this implementation
template<class Impl, class T = Impl, class TInt = T>
class CSingletonHelper
{
public:
    CSingletonHelper() {}
    virtual ~CSingletonHelper() {}

    static TInt& GetInstance()
    {
        static CMockableSingletonPtr<T, TInt> instance{ new Impl() };
        return *CMockableSingletonPtr<T, TInt>::GetRefToSingletonPtr();
    }

private:
    CSingletonHelper(const CSingletonHelper& rhs); // forbid copy constructor
    CSingletonHelper& operator=(const CSingletonHelper& rhs); // forbid assignment construction
};

