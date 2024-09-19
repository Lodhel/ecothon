package com.example.mgc

import com.yandex.mapkit.geometry.Point

data class Plant(
    val name: String = "ШИПОВНИК",
    val description: String = "Кустарник шиповника – это многолетнее растение, принадлежащее к семейству Розовые. Его нередко называют «дикой розой»",
    val age: String = "2 года",
    val state: String = "хорошее",
    val point: Point
)
