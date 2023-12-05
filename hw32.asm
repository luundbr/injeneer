; Author: Ray Doyle
; https://www.doyler.net/security-not-included/hello-world-shellcode

global _start
section .text
_start:
    jmp short call_shellcode

shellcode:
    ; JMP-CALL-POP allows the application to be written without any hardcoded addresses (unlike 'mov ecx, message')
    ; This works because the "CALL" instruction places the address of the next instruction, in case of a return
    ; In this case the next instruction is the "Hello World!" string
    
    ; Move the pointer to the string into ECX off of the stack
    pop ecx

    ; Move the value 4 into EAX (system call for write)
    ; Zeros out the register and then uses al to avoid nulls in the resulting shellcode
    xor eax, eax
    mov al, 0x4

    ; Move the value 1 into EBX (fd1 = STDOUT)
    xor ebx, ebx
    mov bl, 0x1
    
    ; Move the value 13 into EDX (length of "Hello World!\n1")
    xor edx, edx
    mov dl, 13

    ; Send an 0x80 interrupt to invoke the system call
    int 0x80

    ; Exit the program gracefully
        
    ; Move the value 1 into EAX (system call for exit)
    xor eax, eax
    mov al, 0x1

    ; Zero out the EBX register for a successful exit status
    xor ebx, ebx

    ; Send an 0x80 interrupt to invoke the system call
    int 0x80

call_shellcode:
    call shellcode
    message: db "Hello World", 0xA
