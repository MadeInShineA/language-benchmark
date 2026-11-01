package main

import (
	"fmt"
	"os"
	"strconv"
)

type ViewPort struct {
	RealCenter      float64
	ImaginaryCenter float64
	Width           float64
}

func NewViewport(RealCenter float64, ImaginaryCenter float64, Width float64) ViewPort {
	return ViewPort{RealCenter, ImaginaryCenter, Width}

}

func parse_args(args []string) (int, int) {

	if len(args) != 3 {
		fmt.Printf("Usage: %s height width\n", args[0])
		os.Exit(1)
	}

	height, width := args[1], args[2]

	height_int, height_error := strconv.Atoi(height)
	width_int, width_error := strconv.Atoi(width)

	// Check conversion errors
	if height_error != nil || width_error != nil {
		fmt.Println("Error: height and width should be int")
		os.Exit(1)
	}

	return height_int, width_int

}

func create_canvas(height int, width int) [][]int {
	matrix := make([][]int, height)

	for i := range matrix {
		matrix[i] = make([]int, width)
	}
	return matrix
}

func get_viewport(height int, width int)

func calculate_canvas_value(x int, y int) int {
	if (x+y)%2 == 0 {
		return 1
	}
	return 0
}

func set_canvas_value(canvas [][]int, x int, y int, value int) {
	canvas[x][y] = value
}

func main() {

	args := os.Args

	height, width := parse_args(args)

	canvas := create_canvas(height, width)

	for y := range height {
		for x := range width {
			value := calculate_canvas_value(x, y)
			set_canvas_value(canvas, x, y, value)
		}
	}

	fmt.Println(canvas)

}
