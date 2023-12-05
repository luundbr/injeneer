; modified from https://www.doyler.net/security-not-included/hello-world-shellcode

BITS 64
global _start
section .text
_start:
    jmp short call_shellcode

shellcode:
    ; JMP-CALL-POP technique to get the address of the string into rsi
    pop rsi

    ; setup for write (syscall 1)
    xor rax, rax
    mov al, 0x1

    ; stdout (1) into rdi
    xor rdi, rdi
    mov dil, 0x1

    ; len of the message into rdx
    xor rdx, rdx
    mov dl, 13

    ; invoke write
    syscall

    ; setup for exit (syscall 60)
    xor rax, rax
    mov al, 60

    ; exit code 0 in rdi
    xor rdi, rdi

    ; invoke exit
    syscall

call_shellcode:
    call shellcode
    message: db "Hello World", 0xA

