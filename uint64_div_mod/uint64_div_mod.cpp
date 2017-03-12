#include <iostream>

const uint32_t max_uint32 = (uint32_t)(((uint64_t)1 << 32) -1);

uint64_t
divll(uint64_t n, uint32_t b)
{
    uint64_t e = max_uint32 / b;
    uint32_t r2 = max_uint32 % b;
    uint64_t r = n;
    uint64_t m = 0;

    if (b == 0)
        return max_uint32 / b;
    
    if (n <= max_uint32)
        return ((uint32_t)n) / b;

    do
    {
        uint32_t p1 = (uint32_t)((r >> 32) & max_uint32);
        uint32_t p2 = (uint32_t)(r & max_uint32);

        uint64_t c = p2 / b;
        uint32_t r3 = p2 % b;

        uint64_t d = p1 / b;
        uint32_t r1 = p1 % b;

        r = (uint64_t)r1 * (uint64_t)r2 + r1 + r3;
        m += (d << 32) + r1 * e + c;
    }
    while (r >= b);

    return m;
}

uint64_t
modll(uint64_t n, uint32_t b)
{
    return n - b * divll(n, b);
}

uint64_t
divll64(uint64_t n, uint64_t d)
{
    uint64_t final_q = 0;
    uint64_t r = n;

    if (d == 0)
        return max_uint32 / d;
    
    if (n < d) return 0;

    do
    {
        uint64_t q = 1;
        uint64_t tmp_n = r, tmp_d = d, tmp_last_d = d;

        while(tmp_n >= d)
        {
            tmp_n >>= 1;
            q <<= 1;
            tmp_last_d = tmp_d;
            tmp_d <<= 1;
        }

        q >>= 1;

        r -= tmp_last_d;
        final_q += q;
    } while (r >= d);

    return final_q;
}

uint64_t
modll64(uint64_t n, uint64_t d)
{
    return n - d * divll64(n, d);
}

int main()
{
    uint64_t p = (uint64_t)(((uint64_t)0xF) << 59) + max_uint32;
    uint32_t d = 10;

    std::cout << p << " / " << d
              << "=" << (p / d)
              << "," << divll64(p, d)
              << "," << p << "%" << d
              << "=" << (p % d)
              << "," << modll(p, d)
              << ",p is uint64_t:" << (p>max_uint32)
              << std::endl;

    uint64_t dd = ((uint64_t)1) << 32;

    std::cout << p << " / " << dd
              << "=" << (p / dd)
              << "," << divll64(p, dd)
              << "," << p << "%" << dd
              << "=" << (p % dd)
              << "," << modll64(p, dd)
              << ",p is uint64_t:" << (p>max_uint32)
              << std::endl;

    uint64_t ddd = p;

    std::cout << p << " / " << ddd
              << "=" << (p / ddd)
              << "," << divll64(p, ddd)
              << "," << p << "%" << ddd
              << "=" << (p % ddd)
              << "," << modll64(p, ddd)
              << ",p is uint64_t:" << (p>max_uint32)
              << std::endl;
    
    uint64_t dddd = 1;

    std::cout << p << " / " << dddd
              << "=" << (p / dddd)
              << "," << divll64(p, dddd)
              << "," << p << "%" << dddd
              << "=" << (p % dddd)
              << "," << modll64(p, dddd)
              << ",p is uint64_t:" << (p>max_uint32)
              << std::endl;
}
