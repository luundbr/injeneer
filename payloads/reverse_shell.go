package main

import (
	"fmt"
	"net"
	"os"
)

var HOST = "127.0.0.1"
var PORT = "8999"

func main() {
	// Specify the host and port to connect to

	// Connect to the remote server
	conn, err := net.Dial("tcp", HOST+":"+PORT)
	if err != nil {
		fmt.Println("Error connecting:", err.Error())
		os.Exit(1)
	}

	// Send a message to the server
	_, err = conn.Write([]byte("Hello, server!\n"))
	if err != nil {
		fmt.Println("Error sending message:", err.Error())
		conn.Close()
		os.Exit(1)
	}

	fmt.Println("Message sent to server successfully")

	// Close the connection when done
	conn.Close()
}
