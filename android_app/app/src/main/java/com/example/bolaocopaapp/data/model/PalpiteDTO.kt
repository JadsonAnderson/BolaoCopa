package com.example.bolaocopaapp.data.model

import com.google.gson.annotations.SerializedName

data class PalpiteDTO(
    @SerializedName("partida_id")
    val partidaId: Int,

    @SerializedName("gols_a")
    val golsA: Int,

    @SerializedName("gols_b")
    val golsB: Int
)
