#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define PORT 0
#define IP 0

int main() {
    const char* server_ip = IP;
    const int server_port = PORT;

    struct sockaddr_in server_address;
    memset(&server_address, 0, sizeof(server_address));
    server_address.sin_family = AF_INET;

    // Converts an ip from presentation (string) to network (binary)
    inet_pton(AF_INET, server_ip, &server_address.sin_addr);

    server_address.sin_port = htons(server_port);

    // Create a socket
    int sock = socket(PF_INET, SOCK_STREAM, 0);
    if (sock == -1) {
        perror("socket");
        return EXIT_FAILURE;
    }

    // Connect to the server
    if (connect(sock, (struct sockaddr*)&server_address, sizeof(server_address)) == -1) {
        perror("connect");
        return EXIT_FAILURE;
    }

    // Send data
    const char* data_to_send = "Hello, server!";
    if (send(sock, data_to_send, strlen(data_to_send), 0) == -1) {
        perror("send");
        return EXIT_FAILURE;
    }

    printf("Message sent to server successfully\n");

    close(sock);

    return EXIT_SUCCESS;
}
