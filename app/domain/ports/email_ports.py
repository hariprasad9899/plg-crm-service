from abc import ABC, abstractmethod


class EmailPort:

    @abstractmethod
    def send_email():
        pass
