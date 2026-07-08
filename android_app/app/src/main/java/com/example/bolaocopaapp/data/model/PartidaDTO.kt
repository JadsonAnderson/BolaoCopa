package com.example.bolaocopaapp.data.model

import com.google.gson.annotations.SerializedName

data class PartidaDTO(
    @SerializedName("id")
    val id: Int,

    @SerializedName("time_a")
    val timeA: String,

    @SerializedName("time_b")
    val timeB: String,

    @SerializedName("bandeira_a")
    val bandeiraA: String,

    @SerializedName("bandeira_b")
    val bandeiraB: String,

    @SerializedName("data_jogo")
    val dataJogo: String
)
