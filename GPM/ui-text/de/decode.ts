export const decode = {
  title: "Decodieren",
  lead: "Substanz S und Index I eingeben — das System rekonstruiert das Wort Schritt für Schritt (normalisierte Form, Großbuchstaben, ß bleibt ß).",
  guide:
    "Hier brauchst du die beiden Zahlen aus dem Encodieren: Substanz S und Index I. Nach dem Decodieren siehst du die normalisierte Form — also Großbuchstaben, ß bleibt ß. Ob du ursprünglich Müller oder MUELLER eingegeben hattest, erkennt man aus S und I allein nicht; dafür müsste die Originalschreibweise mitgespeichert sein (Datenbank oder .gpm).",
  substanceLabel: "Substanz S",
  indexLabel: "Index I",
  substancePlaceholder: "z.B. 372945",
  indexPlaceholder: "z.B. 13",
  submit: "Decodieren",
  tip: "Tipp: Erst ein Wort encodieren, dann S und I hier einfügen — oder „S & I zum Decodieren“ im Encodieren-Tab nutzen.",
  resultTitle: "Rekonstruktion",
  word: "Wort",
  empty: "S und I eingeben.",
} as const;
