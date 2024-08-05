#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/time.h>

#define SERVER_IP "127.0.0.1" // Replace with your server's IP address
#define PORT 12000
#define MAX_BUFFER_SIZE 1024
#define MAX_PING_COUNT 10   // Number of pings to send
#define TIMEOUT_SECONDS 1  // Timeout in seconds

int main() {
    int clientSocket;
    struct sockaddr_in serverAddress;

    // Create UDP socket
    if ((clientSocket = socket(AF_INET, SOCK_DGRAM, 0)) == -1) {
        perror("Error creating socket");
        exit(1);
    }

    memset(&serverAddress, 0, sizeof(serverAddress));
    serverAddress.sin_family = AF_INET;
    serverAddress.sin_addr.s_addr = inet_addr(SERVER_IP);
    serverAddress.sin_port = htons(PORT);

    char buffer[MAX_BUFFER_SIZE];
    struct timeval timeout;
    timeout.tv_sec = TIMEOUT_SECONDS;
    timeout.tv_usec = 0;

    for (int sequence_number = 1; sequence_number <= MAX_PING_COUNT; sequence_number++) {
        // Construct the ping message with sequence number and timestamp
        struct timeval current_time;
        gettimeofday(&current_time, NULL);
        snprintf(buffer, sizeof(buffer), "ping %d %ld", sequence_number, current_time.tv_sec); // Use snprintf to prevent buffer overflow

        printf("Sending: %s\n", buffer);

        // Set socket timeout
        if (setsockopt(clientSocket, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout)) < 0) {
            perror("Error setting socket timeout");
            close(clientSocket);
            exit(1);
        }

        // Send data to the server
        if (sendto(clientSocket, buffer, strlen(buffer), 0, (struct sockaddr *)&serverAddress, sizeof(serverAddress)) == -1) {
            perror("Error sending data");
            close(clientSocket);
            exit(1);
        }

        // Receive response from the server
        int bytesReceived = recvfrom(clientSocket, buffer, MAX_BUFFER_SIZE, 0, NULL, NULL);

        if (bytesReceived == -1) {
            printf("Timeout: No response received for sequence number %d\n", sequence_number);
        } else {
            buffer[bytesReceived] = '\0';
            printf("Received from server: %s\n", buffer);
        }

        sleep(1); // Wait for 1 second before sending the next ping
    }

    close(clientSocket);
    return 0;
}
