package com.example.cirurgiasegura_fala.network

import com.example.cirurgiasegura_fala.network.TranscriptionApi
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.io.File

data class TranscriptionResponse(
    val text: String
)

val retrofit = Retrofit.Builder()
    //.baseUrl("http://SEU_SERVIDOR:8000")
    .baseUrl("https://processarpdffalatex.zapto.org")
    .addConverterFactory(GsonConverterFactory.create())
    .build()

val api = retrofit.create(TranscriptionApi::class.java)




suspend fun enviarParaWhisper(path: String, token: String): String? {
    val file = File(path)
    if (!file.exists()) return "Arquivo não encontrado"

    // O MediaType deve ser o mesmo usado no AudioRecorder (m4a)
    val request = file.asRequestBody("audio/m4a".toMediaType())

    // IMPORTANTE: O primeiro parâmetro "file" deve ser o nome que o seu
    // servidor espera no @Part do backend.
    val multipart = MultipartBody.Part.createFormData("file", file.name, request)

    /*
    val response = api.transcribeAudio(multipart)
    return response.body()?.text
     */

    return try {
        val response = api.transcribeAudio(token, multipart)
        if (response.isSuccessful) {
            response.body()?.text
        } else {
            "Erro no servidor: ${response.code()}"
        }
    } catch (e: Exception) {
        "Falha na conexão: ${e.message}"
    }
}
