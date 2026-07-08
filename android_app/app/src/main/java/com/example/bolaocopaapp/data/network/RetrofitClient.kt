package com.example.bolaocopaapp.data.network

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object RetrofitClient {
    // 10.0.2.2 é o endereço que o emulador do Android usa para acessar o localhost do PC.
    private const val BASE_URL = "http://10.0.2.2:8000/"

    val apiService: BolaoAPIService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(BolaoAPIService::class.java)
    }
}