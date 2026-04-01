package com.example.cirurgiasegura_fala.services

import android.media.MediaRecorder
import android.content.Context
import java.io.File

class AudioRecorder(private val context: Context) {
    private var recorder: MediaRecorder? = null
    private lateinit var outputFile: File

    fun start(): String {
        outputFile = File(context.cacheDir, "audio.m4a")

        recorder = MediaRecorder().apply {
            setAudioSource(MediaRecorder.AudioSource.MIC)
            setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
            setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
            setOutputFile(outputFile.absolutePath)
            prepare()
            start()
        }
        return outputFile.absolutePath
    }

    fun stop(): String {
        recorder?.apply {
            stop()
            release()
        }
        recorder = null
        return outputFile.absolutePath
    }

}