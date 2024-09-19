class Negados:
    def __init__(self):
        self.negados = {
            223344556: "Juan Carlos",
            665544332: "Rafaela Silva",
            778899001: "Renata dos Santos"
        }

    def __contains__(self, tag):
        return tag in self.negados

    def __getitem__(self, tag):
        return self.negados.get(tag)

    def adicionarNegacao(self, tag, nome):
        self.negados[tag] = nome

    def removerNegacao(self, tag):
        if tag in self.negados:
            del self.negados[tag]