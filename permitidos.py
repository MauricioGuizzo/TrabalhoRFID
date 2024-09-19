class Permitidos:
    def __init__(self):
        self.autorizados = {
            123456789: "Israel Renan",
            987654321: "Paulo Schnaider",
            555666777: "Rafael Souza"
        }

    def __contains__(self, tag):
        return tag in self.autorizados

    def __getitem__(self, tag):
        return self.autorizados.get(tag)

    def adicionarAutorizacao(self, tag, nome):
        self.autorizados[tag] = nome

    def removerAutorizacao(self, tag):
        if tag in self.autorizados:
            del self.autorizados[tag]
