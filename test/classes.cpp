class Rectangle: public Geometry {
    int width, height;
    public:
    void set_values (int,int);
    int area() {
        return width*height;
    }
    private:
    void change_values (int,int);
    int cicumference() {
        return (width+height) * 2;
    }
} R, Rect;


void Rectangle::set_values (int x, int y) {
    width = x;
    height = y;
}
