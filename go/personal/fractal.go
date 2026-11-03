package main

import (
	"fmt"
	"image"
	"image/color"
	"image/png"
	"math"
	"os"
	"strconv"
)

type ViewPort struct {
	RealCenter      float64
	ImaginaryCenter float64
	Height          float64
	Width           float64
}

func parseArgs(args []string) (int, int, string) {

	if len(args) != 4 {
		fmt.Printf("Usage: %s height width filename\n", args[0])
		os.Exit(1)
	}

	height, width, filename := args[1], args[2], args[3]

	height_int, height_error := strconv.Atoi(height)
	width_int, width_error := strconv.Atoi(width)

	// Check conversion errors
	if height_error != nil || width_error != nil {
		fmt.Println("Error: height and width should be int")
		os.Exit(1)
	}

	return height_int, width_int, filename

}

func createCanvas(height int, width int) []int {
	return make([]int, height*width)

}

func setCanvasValue(canvas []int, x int, y int, width, value int) {
	canvas[y*width+x] = value
}

func pixelToComplex(x int, y int, height int, width int, view_port ViewPort) (float64, float64) {
	real := view_port.RealCenter + (float64(x)/float64(width)-0.5)*view_port.Width
	imaginary := view_port.ImaginaryCenter + (float64(y)/float64(height)-0.5)*view_port.Height

	return real, imaginary
}

func mandelbrot(c_real float64, c_imaginary float64, maxIter int) int {
	z_real, z_imaginary := 0.0, 0.0

	for i := 0; i < maxIter; i += 1 {
		if z_real*z_real+z_imaginary*z_imaginary > 4.0 {
			return i
		}
		z_real, z_imaginary = z_real*z_real-z_imaginary*z_imaginary+c_real, 2*z_real*z_imaginary+c_imaginary
	}
	return maxIter
}

func render(values []int, height, width, maxIter int) *image.RGBA {
	img := image.NewRGBA(image.Rect(0, 0, width, height))
	for y := 0; y < height; y++ {
		for x := 0; x < width; x++ {
			img.Set(x, y, palette(values[y*width+x], maxIter))
		}
	}
	return img
}

func palette(n, maxIter int) color.RGBA {
	if n == maxIter {
		return color.RGBA{0, 0, 0, 255}
	}
	t := math.Log(float64(n)+1) / math.Log(float64(maxIter)+1)
	return color.RGBA{
		R: uint8(255 * t),
		G: uint8(255 * t),
		B: uint8(128 + 127*t),
		A: 255,
	}
}

func savePNG(img *image.RGBA, filename string) {
	f, err := os.Create(filename)
	if err != nil {
		fmt.Println("Error creating file:", err)
		os.Exit(1)
	}
	defer f.Close()

	if err := png.Encode(f, img); err != nil {
		fmt.Println("Error encoding PNG:", err)
		os.Exit(1)
	}
	fmt.Println("Saved", filename)
}

func main() {

	args := os.Args

	height, width, filename := parseArgs(args)

	view_port := ViewPort{RealCenter: -0.5, ImaginaryCenter: 0.0, Height: 2.5, Width: 2.5}

	maxIter := 1000

	canvas := createCanvas(height, width)

	for y := range height {
		for x := range width {
			c_real, c_imaginary := pixelToComplex(x, y, width, height, view_port)
			value := mandelbrot(c_real, c_imaginary, maxIter)
			setCanvasValue(canvas, x, y, width, value)
		}
	}

	image := render(canvas, height, width, maxIter)
	savePNG(image, filename)
}
