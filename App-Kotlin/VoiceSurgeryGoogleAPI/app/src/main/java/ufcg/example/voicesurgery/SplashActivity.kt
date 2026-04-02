package ufcg.example.voicesurgery

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import ufcg.example.voicesurgery.databinding.ActivitySplashBinding

class SplashActivity : AppCompatActivity() {

    private lateinit var binding: ActivitySplashBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySplashBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Ao clicar em "Iniciar preenchimento", vai para WelcomeActivity (Tela 2)
        binding.btnStart.setOnClickListener {
            val intent = Intent(this, WelcomeActivity::class.java)
            startActivity(intent)
        }
    }
}
