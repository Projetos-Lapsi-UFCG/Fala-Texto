package com.example.cirurgiasegura_fala.network

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import okhttp3.OkHttpClient
import java.util.concurrent.TimeUnit

// Usamos um 'object' para criar um Singleton (uma única instância)
object ApiClient {

    private const val BASE_URL = "https://processarpdffalatex.zapto.org"


    // Configurar o Cliente HTTP com tempos maiores
    private val okHttpClient: OkHttpClient by lazy {
        OkHttpClient.Builder()
            .connectTimeout(60, TimeUnit.SECONDS) // Tempo para conectar ao servidor
            .writeTimeout(60, TimeUnit.SECONDS)   // Tempo para enviar o arquivo de áudio
            .readTimeout(90, TimeUnit.SECONDS)    // Tempo para esperar a resposta (transcrição)
            .build()
    }

    // 'lazy' garante que o Retrofit só seja criado quando for usado pela 1ª vez
    private val retrofit: Retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    // Exposição pública do serviço já criado
    val apiService: ApiService by lazy {
        retrofit.create(ApiService::class.java)
    }

    // Adicione esta linha para centralizar
    val transcriptionApi: TranscriptionResponse by lazy { retrofit.create(TranscriptionResponse::class.java) }
}