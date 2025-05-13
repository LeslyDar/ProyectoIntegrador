from cli import CLI


def main():
    """Función principal que ejecuta el simulador del SO"""
    cli = CLI()

    while True:
        cli.show_menu()
        option = input("Seleccione una opción: ")

        if option == "1":
            cli.create_process_interactive()
        elif option == "2":
            cli.list_processes_table()
        elif option == "3":
            cli.show_resources()
        elif option == "4":
            cli.change_algorithm()
        elif option == "5":
            cli.run_simulation()
        elif option == "6":
            cli.suspend_process()
        elif option == "7":
            cli.resume_process()
        elif option == "8":
            cli.terminate_process()
        elif option == "9":
            cli.show_logs()
        elif option == "10":
            cli.send_message()
        elif option == "11":
            cli.view_messages()
        elif option == "12":
            cli.run_producer_consumer()
        elif option == "0":
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida. Intente nuevamente.")


if __name__ == "__main__":
    main()