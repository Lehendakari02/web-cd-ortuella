/* ==========================================================================
   CONTENIDO DEL CLUB (lo que se escribe a mano)
   - Partidos, resultados, clasificaciones y goleadores NO van aquí: llegan
     solos de la Federación en el archivo datos-federacion.js.
   - Lo que lleva  pendiente: true  está por completar.
   ========================================================================== */

window.CLUB = {
  noticias: [
    { fecha: "2026-10-18", etiqueta: "Primer equipo", foto: "img/campo.jpg",
      titulo: "Empate sin goles en Sopuerta",
      texto: "El primer equipo suma un punto en Santa Ana (0-0) en la quinta jornada y sigue cuarto con 10 puntos. El domingo 25 recibimos al Gazteak en Otxartaga Berri." },
    { fecha: "2026-06-01", etiqueta: "Club", foto: "img/entrada.jpg",
      titulo: "Abiertas las inscripciones para la temporada 2026/27",
      texto: "Niños, niñas y jóvenes que quieran jugar en el Ortuella pueden apuntarse llamando al 696 51 24 69 o escribiéndonos por redes sociales." },
    { fecha: "2024-09-01", fechaTexto: "Otoño 2024", etiqueta: "Historia", foto: "img/tribuna.jpg",
      titulo: "75 años de fútbol en Ortuella",
      texto: "Con motivo del 75 aniversario, el club organizó en la Kultur Etxea la exposición «Un paseo por la historia del Club y del fútbol regional vizcaíno»." },
    { fecha: "2022-04-03", etiqueta: "Fútbol base", foto: "img/cadete-campeon.jpg",
      titulo: "El Cadete, campeón de liga y ascenso a Primera",
      texto: "Gran temporada 2021/22 de nuestros cadetes, que se proclamaron campeones y lograron el ascenso a Primera División." }
  ],

  // Convocatoria del primer equipo en su último partido (acta de la jornada 5)
  primerEquipo: {
    partido: "Jornada 5 · Sopuerta 0-0 Ortuella",
    titulares: [
      [23, "Aitzol Coloma Colina"], [2, "Ander García Antúnez"], [3, "Julen Gago Ruiz"],
      [4, "Aitor Periáñez Rodríguez"], [5, "Izotz Esteban Llinares"], [6, "Aritz De María López"],
      [7, "Asier Totorica Castellanos"], [8, "Julen Martínez Gutiérrez"], [9, "Endika Lorenzo Quintanar"],
      [10, "Gorka González Bustamante"], [11, "Ibai Acosta Dos Santos"]
    ],
    suplentes: [
      [1, "Asier Martínez Lombera"], [12, "Eneko Cabezas Cuesta"], [14, "Eder Almeida Ranedo"],
      [15, "Aritz Martín Valderrama"], [16, "Oier Romero Marcos"], [17, "Sergio Ureta Lombera"],
      [18, "Gorka Iglesias González"], [19, "Eder Vico Fuente"], [20, "Yeray Rincón González"]
    ],
    cuerpoTecnico: [
      ["Entrenador", "Gorka Prieto Feliz"], ["Segundo entrenador", "Juan Luis Coloma Pérez"], ["Delegado", "Endika Pascual"]
    ]
  },

  // Equipos sin datos en la Federación (fútbol base escolar)
  equiposBase: [
    { nombre: "Infantil", categoria: "Infantil Liga D (Bizkaia) · nacidos 2013-14" },
    { nombre: "Alevín", categoria: "Deporte escolar", pendiente: true },
    { nombre: "Benjamín", categoria: "Deporte escolar", pendiente: true }
  ],

  directiva: [
    ["Presidente", "José Ramón Bayón"], ["Vicepresidente", "Manuel Rodríguez"],
    ["Secretaria", "Rakel Chico"], ["Tesorero", "Fernando Chico"],
    ["Coordinador", "César Guadilla"], ["Vocal", "Juan Luis Coloma"], ["Vocal", "Javier Rincón"],
    ["Presidente Otxartaga", "Aitor Valle"], ["Vicepresidente Otxartaga", "Endika Pascual"],
    ["Secretario Otxartaga", "Iker Bartolomé"]
  ],

  socio: { precio: "50 €", periodo: "al año", otros: [["Jubilados", "25 €"]] },
  // Precios de la web antigua: confirmar si siguen vigentes
  entradas: [["Senior", "7 €"], ["Juvenil", "4 €"], ["Cadete", "3 €"]],

  tienda: [
    { nombre: "Camiseta 75 aniversario", precio: "30 €", foto: null },
    { nombre: "Bufanda del club", precio: "15 €", foto: null },
    { nombre: "Paraguas", precio: null, foto: "img/paraguas.jpg" },
    { nombre: "Pin del escudo", precio: null, foto: "img/pin.jpg" }
  ],

  patrocinadores: [
    { nombre: "Markofer · Montajes y mantenimientos", logo: "img/markofer.png" }
  ],
  colaboradores: ["Ortuellako Udala · Ayuntamiento de Ortuella", "Bizkaiko Foru Aldundia · Diputación Foral de Bizkaia",
                  "Federación Vizcaína de Fútbol", "Athletic Club Fundazioa"]
};
