/* ==========================================================================
   CONTENIDO DEL CLUB (lo que se escribe a mano)
   - Partidos, resultados, clasificaciones y goleadores NO van aquí: llegan
     solos de la Federación en el archivo datos-federacion.js.
   - Lo que lleva  pendiente: true  está por completar.
   ========================================================================== */

window.CLUB = {
  // Destacado de la portada: una sola novedad importante que se alterna (gira) con
  // el texto del club. Para quitarlo: destacado: null. "hasta": deja de salir ese día.
  destacado: {
    etiqueta: "Ya a la venta",
    titulo: "Camiseta del 75 aniversario",
    texto: "Edición especial por los 75 años del club. 30 €.",
    foto: "img/camiseta-75-recorte.webp",
    boton: "Cómprala aquí",
    enlace: "tienda.html",
    hasta: null
  },

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
      titulo: "El Cadete gana la liga y sube a Primera",
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
  // Plantilla de cada equipo (de las capturas de la app de la Federación). Ejemplo:
  // juvenil: { jugadores: [[1, "Nombre Apellido", "Porteros"], [4, "Nombre Apellido", "Defensas"]], tecnicos: [["Entrenador", "Nombre"]] }
  // Plantillas sacadas de la app de la Federación (capturas de Julen, 21-10). El fútbol base, cuando se publiquen.
  // Los porteros salen de la tabla de porteros de la Federación; los demás van como "Jugadores" (la app no da demarcación).
  plantillas: {
    primer: {
      jugadores: [
        [null, "Ibai Acosta dos Santos", "Jugadores"],
        [null, "Eder Almeida Ranedo", "Jugadores"],
        [null, "Eneko Cabezas Cuesta", "Jugadores"],
        [null, "Aitzol Coloma Colina", "Porteros"],
        [null, "Ander Elices Patiño", "Jugadores"],
        [null, "Izotz Esteban Llinares", "Jugadores"],
        [null, "Julen Gago Ruiz", "Jugadores"],
        [null, "Ander Garcia Antunez", "Jugadores"],
        [null, "Gorka Gonzalez Bustamante", "Jugadores"],
        [null, "Gorka Iglesias Gonzalez", "Jugadores"],
        [null, "Aitor Lombera Agra", "Jugadores"],
        [null, "Endika Lorenzo Quintanar", "Jugadores"],
        [null, "Aritz Martin Valderrama", "Jugadores"],
        [null, "Julen Martinez Gutierrez", "Jugadores"],
        [null, "Asier Martinez Lombera", "Porteros"],
        [null, "Aitor Periañez Rodriguez", "Jugadores"],
        [null, "Oier Romero Marcos", "Jugadores"],
        [null, "Asier Totorica Castellanos", "Jugadores"],
        [null, "Sergio Ureta Lombera", "Jugadores"],
        [null, "Lander Vaquero Vazquez", "Jugadores"],
        [null, "Eder Vico Fuente", "Jugadores"]
      ],
      tecnicos: [["Entrenador", "Gorka Prieto Feliz"], ["Entrenador", "Juan L Coloma Perez"], ["Entrenador", "Endika Pascual Sanchez"], ["Delegado", "Juan Carlos Puertas Trasahedo"], ["Delegado", "Endika Sanchez Caro"]]
    },
    b: {
      jugadores: [
        [null, "Iker Bartolomé Nieto", "Jugadores"],
        [null, "Landing Bayo", "Jugadores"],
        [null, "Oier de Diego Ulibarri", "Jugadores"],
        [null, "Aritz de Maria Lopez", "Jugadores"],
        [null, "Endika Diaz Perez", "Jugadores"],
        [null, "Jon Ander Diez Gonzalez", "Jugadores"],
        [null, "Angelo Cristiano Geremias da Silva", "Jugadores"],
        [null, "Xabier Gonzalez Lopez", "Jugadores"],
        [null, "Iker Guadilla Estevez", "Jugadores"],
        [null, "Kevin Guadilla Estevez", "Jugadores"],
        [null, "Gonzalo Iglesias Tamayo", "Porteros"],
        [null, "Youssouf Jaiteh", "Jugadores"],
        [null, "Yusupha Janneh", "Jugadores"],
        [null, "Maren Lafuente Ibinaga", "Jugadores"],
        [null, "Illan Martin Espino", "Jugadores"],
        [null, "Unai Martinez Lansorena", "Jugadores"],
        [null, "Xabel Menendez Vaz", "Jugadores"],
        [null, "Endika Pascual Sanchez", "Jugadores"],
        [null, "Yeray Rincon Gonzalez", "Jugadores"],
        [null, "Joseba Santurtun Molinero", "Jugadores"],
        [null, "Julen Uria Abasolo", "Jugadores"],
        [null, "Alain Vazquez Gutierrez", "Jugadores"]
      ],
      tecnicos: [["Entrenador", "Paul Acosta Domínguez"], ["Delegado", "Aitor Valle Ogazon"]]
    },
    juvenil: {
      jugadores: [
        [null, "Julen Agredano Gayoso", "Jugadores"],
        [null, "Jon Alonso-Mardones Alvarez", "Jugadores"],
        [null, "Julen Aparicio Esteban", "Jugadores"],
        [null, "Iker de los Mozos Romay", "Jugadores"],
        [null, "Adur Erdozain Lopez", "Jugadores"],
        [null, "Roberto Erraiz Iglesias", "Jugadores"],
        [null, "Xabier Fernandez Segador", "Jugadores"],
        [null, "Alvaro Fernandez Tarrio", "Jugadores"],
        [null, "Izei Gomez Galan", "Porteros"],
        [null, "Unai Guerrero Barrios", "Jugadores"],
        [null, "Aitor Herrero Campos", "Jugadores"],
        [null, "Aritz Iglesias Miguelez", "Jugadores"],
        [null, "Urko Martin Santisteban", "Jugadores"],
        [null, "Aingeru Moriña Rivera", "Porteros"],
        [null, "Eneko Novelle Llorente", "Jugadores"],
        [null, "Aitor Ouro Barcia", "Jugadores"],
        [null, "Tasio Sagastizabal Garcia", "Jugadores"],
        [null, "Ibai Sevilla Cano", "Jugadores"],
        [null, "Alain Zugazabeitia Fernández", "Jugadores"]
      ],
      tecnicos: [["Entrenador", "Oier Romero Marcos"], ["Delegado", "Jokin Garcia Martinez"]]
    },
    cadete: {
      jugadores: [
        [2, "Iñigo Rodriguez Ramirez", "Jugadores"],
        [3, "Ibai Gonzalez Llanos", "Jugadores"],
        [4, "David Sanchez Terrazas", "Jugadores"],
        [5, "Ander Fernandez Avellanal", "Jugadores"],
        [6, "Enaitz Gonzalez Delgado", "Jugadores"],
        [7, "Aratz Guezuraga Larrea", "Jugadores"],
        [8, "Unai Pinillos Carracedo", "Jugadores"],
        [9, "Asier Marquez Fernandez", "Jugadores"],
        [10, "Peio Salgado Carbo", "Jugadores"],
        [11, "Unai García Angulo", "Jugadores"],
        [12, "Iker Alzueta Mendez", "Jugadores"],
        [13, "Hector Perez Diez", "Porteros"],
        [14, "Aimar Martin Espino", "Jugadores"],
        [15, "Xabier Agredano Manzano", "Jugadores"],
        [17, "Xabier Fernandez Avellanal", "Jugadores"],
        [18, "Iker Alonso Ruiz", "Jugadores"],
        [20, "Jon de Brito Fernandez", "Jugadores"],
        [23, "Izei Izagirre Iriondo", "Jugadores"]
      ],
      tecnicos: [["Entrenador", "Ugaitz Isla Turuelo"], ["Delegado", "Unai Hernando Garcia"]]
    }
  },

  // Foto de cada equipo en su página (carpeta img/equipos/). Ejemplo: cadete: "img/equipos/cadete.jpg"
  fotosEquipos: {},

  equiposBase: [
    { nombre: "Infantil", categoria: "Infantil Liga D (Bizkaia) · nacidos 2013-14" },
    { nombre: "Alevín", categoria: "Alevín Liga B (Bizkaia)", pendiente: true }
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
    { nombre: "Camiseta 75 aniversario", precio: "30 €", foto: "img/camiseta-75.webp" },
    { nombre: "Bufanda 75 aniversario", precio: "15 €", foto: "img/bufanda.webp" },
    { nombre: "Paraguas", precio: null, foto: "img/paraguas.jpg" },
    { nombre: "Pin del escudo", precio: null, foto: "img/pin.jpg" }
  ],

  // Patrocinadores y colaboradores: los de la web antigua del club + los que salen en las
  // publicaciones de Instagram (logos sacados de las plantillas de Canva, redes/canva/).
  // logo: null -> sale el nombre en una ficha hasta tener el logo bueno.
  patrocinadores: [
    { nombre: "Tesoralia", detalle: null, logo: "img/patrocinadores/tesoralia.webp", web: null },
    { nombre: "Markofer", detalle: "Montajes y mantenimientos", logo: "img/markofer.webp", web: null },
    { nombre: "Euskadi LowCost", detalle: null, logo: "img/patrocinadores/euskadi-lowcost.webp", web: null },
    { nombre: "Restaurante Sukalde", detalle: "Restaurante", logo: "img/patrocinadores/sukalde.webp", web: null },
    { nombre: "Irish Pub Black & White", detalle: "Irish pub · desde 1991", logo: "img/patrocinadores/irish-pub.webp", web: null },
    { nombre: "Academia Siglo XXIII", detalle: "Academia · Ortuella", logo: null, web: null },
    { nombre: "Andamios y Montacargas Europa", detalle: "Andamios · Ortuella", logo: "img/patrocinadores/andamios-europa.webp", web: null }
  ],
  colaboradores: [
    { nombre: "Ayuntamiento de Ortuella", detalle: "Ortuellako Udala", logo: "img/patrocinadores/ayuntamiento-ortuella.webp", web: "https://www.ortuella.eus/" },
    { nombre: "Diputación Foral de Bizkaia", detalle: "Bizkaiko Foru Aldundia", logo: "img/patrocinadores/bizkaia.webp", web: "https://web.bizkaia.eus/es/inicio" },
    { nombre: "Federación Vizcaína de Fútbol", detalle: "Bizkaiko Futbol Federazioa", logo: "img/patrocinadores/fvf.webp", web: "https://www.fvf-bff.eus/" },
    { nombre: "Athletic Club Fundazioa", detalle: "Fundación Athletic Club", logo: null, web: "https://www.athletic-club.eus/" },
    { nombre: "Ekipaciones", detalle: "Tienda online oficial del club", logo: null, web: "https://www.latiendademiclub.com/cdortuella/" }
  ]
};
