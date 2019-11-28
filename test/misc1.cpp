#include <iostream>
#include <string>

using namespace std;

struct cars {
    string model;
    string make;
    int year;
    string plates;
} trucks;


class Z {
} z, b;

class Geometry {
    virtual float area ();
    virtual float circumference();
};

class Circle: public Geometry {

    public:
        Circle();
        ~Circle();
        float radius;
        void set_radius (float);
        float area();
        float circumference();

    private:
        void areaToRadius (float);

} dot;

Circle::Circle() {
}

~Circle::Circle() {
}

float Circle::area() {
    return M_PI * radius*radius;
}

float Circle::circumference() {
    return 2.f * M_PI * radius;
}


void select(char p) {
    switch(p) {
        case 'd':
            break;
        case 'a':
            break;
        case 'b':
            break;
        default:
            break;
    }
}


enum days {
    Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday
};
