package com.example.cirurgiasegura_fala.network

import okhttp3.MultipartBody
import retrofit2.Response
import retrofit2.http.Header
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part

interface TranscriptionApi {

    @Multipart
    @POST("/transcricao")
    suspend fun transcribeAudio(
        @Header("Authorization") token: String, // Adicionado para o JWT
        @Part audio: MultipartBody.Part
        //@Part file: MultipartBody.Part
    ): Response<TranscriptionResponse>
}