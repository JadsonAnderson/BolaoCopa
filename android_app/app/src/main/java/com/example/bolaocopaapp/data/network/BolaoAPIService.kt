package com.example.bolaocopaapp.data.network

import com.example.bolaocopaapp.data.model.PalpiteDTO
import com.example.bolaocopaapp.data.model.PartidaDTO
import retrofit2.Response
import retrofit2.http.*

interface BolaoAPIService {
    @GET("partidas")
    suspend fun getPartidas(): List<PartidaDTO>

    @GET("palpites")
    suspend fun getPalpites(): List<PalpiteDTO>

    @POST("palpites")
    suspend fun enviarPalpite(@Body palpite: PalpiteDTO): Response<Unit>

    @PUT("palpites/{id}")
    suspend fun atualizarPalpite(@Path("id") id: Int, @Body palpite: PalpiteDTO): Response<Unit>

    @DELETE("palpites/{id}")
    suspend fun deletarPalpite(@Path("id") id: Int): Response<Unit>
}