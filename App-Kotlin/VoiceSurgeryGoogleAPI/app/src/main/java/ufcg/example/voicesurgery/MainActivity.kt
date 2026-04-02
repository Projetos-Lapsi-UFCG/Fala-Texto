package ufcg.example.voicesurgery

import android.app.AlertDialog
import android.net.Uri
import android.os.Bundle
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.FrameLayout
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import ufcg.example.voicesurgery.R
import ufcg.example.voicesurgery.data.AuthRepository
import ufcg.example.voicesurgery.data.PdfUploadRepository
import ufcg.example.voicesurgery.services.VoiceCommandProcessor
import ufcg.example.voicesurgery.services.VoiceRecognizer
import ufcg.example.voicesurgery.ui.AnswerExtractor
import ufcg.example.voicesurgery.ui.QuestionViewFactory
import ufcg.example.voicesurgery.utils.CsvDataSaver
import ufcg.example.voicesurgery.utils.FileUtil
import ufcg.example.voicesurgery.utils.PermissionManager
import ufcg.example.voicesurgery.viewmodel.QuizStateManager
import ufcg.example.voicesurgery.ui.PdfFlowManager
import java.io.File

class MainActivity : AppCompatActivity() {
    annotation class LoginResponse

    //Parou, jogador
    private var campoSelecionado: EditText? = null


    // Gerenciadores e Serviços
    private lateinit var progressBar: android.widget.ProgressBar
    private lateinit var progressText: TextView
    private val stateManager = QuizStateManager()
    private lateinit var viewFactory: QuestionViewFactory
    private val answerExtractor = AnswerExtractor()
    private lateinit var dataSaver: CsvDataSaver
    private lateinit var voiceRecognizer: VoiceRecognizer
    private val commandProcessor = VoiceCommandProcessor()

    // Views da UI
    private lateinit var container: FrameLayout
    private lateinit var btnNext: Button
    private lateinit var btnPrevious: Button

    private lateinit var btnFalar: Button

    private lateinit var btnHowto: Button
    private lateinit var textView: TextView
    private lateinit var currentQuestionView: View

    private lateinit var jwtToken: String
    private val authRepository = AuthRepository() // Crie uma instância do repositório

    //private lateinit var dataSaver: CsvDataSaver
    //private lateinit var pdfUploader: PdfUploadRepository

    // --- VARIÁVEIS DE ESTADO ---

    //private var latestCsvFile: File? = null // Para guardar o CSV entre os passo
    /*
    // --- O SELETOR DE PDF FICA NA ACTIVITY ---
    private val pdfPickerLauncher = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        if (uri == null) {
            textView.text = "Seleção de PDF cancelada."
            return@registerForActivityResult
        }

        // 1. Verificamos se temos o CSV salvo
        val csvFile = latestCsvFile
        if (csvFile == null) {
            textView.text = "Erro: Arquivo CSV não encontrado."
            return@registerForActivityResult
        }

        // 2. Copiamos o PDF para um arquivo local
        textView.text = "Processando PDF..."
        val pdfFile = FileUtil.copyPdfToAppStorage(this, uri)
        if (pdfFile == null) {
            textView.text = "Erro ao processar o PDF selecionado."
            return@registerForActivityResult
        }

        // 3. Temos os dois arquivos! Hora de fazer o upload.
        textView.text = "Enviando arquivos..."
        pdfUploader.uploadFiles(jwtToken, csvFile, pdfFile, object : PdfUploadRepository.UploadCallback {
            override fun onSuccess(filePath: String) {
                textView.text = filePath // Ex: "PDF salvo em: /.../preenchido.pdf"
            }

            override fun onError(message: String) {
                textView.text = message // Ex: "Erro na resposta: 404"
            }
        })
    } as (Uri?) -> Unit
    */
    private lateinit var pdfManager: PdfFlowManager



    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Inicializa classes que dependem do Context
        viewFactory = QuestionViewFactory(this)
        dataSaver = CsvDataSaver(this)
        voiceRecognizer = VoiceRecognizer(this)
        // Passamos 'this' (activity), o repositório e uma função lambda para atualizar o texto
        val uploadRepository = PdfUploadRepository(this)

        pdfManager = PdfFlowManager(
            activity = this,
            uploadRepository = uploadRepository,
            onStatusUpdate = { mensagem ->
                // Esta função roda sempre que o Manager quiser falar algo
                textView.text = mensagem
            }
        )

        // Encontra Views
        textView = findViewById(R.id.textView)
        container = findViewById(R.id.question_container)
        btnNext = findViewById(R.id.btn_next)
        btnPrevious = findViewById(R.id.btn_previous)
        btnFalar = findViewById(R.id.btnFalar)
        btnHowto = findViewById(R.id.btnHowto)
        progressBar = findViewById(R.id.progressBar)
        progressText = findViewById(R.id.progressText)

        // Configura Listeners
        btnNext.setOnClickListener { onNextClicked() }
        btnPrevious.setOnClickListener { onPreviousClicked() }
        btnFalar.setOnClickListener { voiceRecognizer.startListening() }
        btnHowto.setOnClickListener { mostraInstrucoes() }

        fazerLogin {
            // Este código aqui (onSuccess) só roda
            // depois que o login for bem-sucedido
            textView.text = "Login feito com sucesso!"
            //Log.d("Login", "Login OK, token pronto para uso.")
            // Você pode, por exemplo, habilitar botões aqui
        }

        setupVoiceListener()

        // Inicia
        PermissionManager.checkAndRequestAudioPermission(this)
        showCurrentQuestion()
        //mostraInstrucoes()
    }

    private fun fazerLogin(onSuccess: () -> Unit) {
        // Mostra o status para o usuário ANTES de começar
        textView.text = "Autenticando..."

        authRepository.login(object : AuthRepository.AuthCallback {

            override fun onSuccess(token: String) {
                // SUCESSO!
                jwtToken = token // Salva o token na Activity
                textView.text = "Login automático realizado" // Atualiza a UI
                onSuccess() // Chama o callback original (ex: habilitar botões)
            }

            override fun onError(message: String) {
                // ERRO!
                textView.text = message // Mostra o erro na UI
            }
        })
    }

    private fun setupVoiceListener() {
        voiceRecognizer.setListener(object : VoiceRecognizer.Listener {
            override fun onReady() { textView.text = "Fale agora..." }
            override fun onListening() { textView.text = "Ouvindo..." }
            override fun onProcessing() { textView.text = "Processando..." }
            override fun onError(error: String) {
                textView.text = error
                // Opcional: reiniciar automaticamente
                // voiceRecognizer.startListening()
            }

            override fun onResult(text: String) {
                textView.text = "Você disse: $text"

                // 1. PRIORIDADE: Se o usuário clicou num campo, preenche direto
                if (campoSelecionado != null) {
                    campoSelecionado?.setText(text)
                    campoSelecionado = null // Limpa para a próxima interação
                    return // Encerra aqui, não processa comandos
                }

                // 2. DEFAULT: Botão falar, usa a lógica de comandos de voz
                val question = stateManager.getCurrentQuestion()
                val shouldGoNext = commandProcessor.processCommand(text, question, currentQuestionView)

                if (shouldGoNext) {
                    //btnNext.performClick()
                    onNextClicked() //Evita dar o balão
                }
            }
        })
    }

    private fun onNextClicked() {
        saveCurrentAnswer()

        if (stateManager.isQuizFinished()) {
            showQuizFinishedDialog()
        } else {
            stateManager.moveToNextQuestion()
            showCurrentQuestion()
        }
    }
    private fun onPreviousClicked() {

        saveCurrentAnswer()
        stateManager.moveToPreviousQuestion()
        showCurrentQuestion()

        /*if (stateManager.isQuizFinished()) {
            showQuizFinishedDialog()
        } else {
            stateManager.moveToNextQuestion()
            showCurrentQuestion()
        }
         */
    }

    // Atualize a função que exibe a questão
    private fun showCurrentQuestion() {
        val question = stateManager.getCurrentQuestion()

        // Pegamos a resposta da questão principal e a função para buscar das subperguntas
        val savedValue = stateManager.getSavedAnswer(question)

        currentQuestionView = viewFactory.createView(
            question,
            container,
            savedValue,
            { subQ -> stateManager.getSavedAnswer(subQ) } // Provedor de respostas para filhos
        )

        container.removeAllViews()
        container.addView(currentQuestionView)
        configurarCliquesNosInputs(currentQuestionView)
        val current = stateManager.getCurrentIndex() + 1
        val total = stateManager.getTotalQuestions()
        progressBar.max = total
        progressBar.progress = current
        progressText.text = "$current/$total"
    }

    private fun saveCurrentAnswer() {
        val question = stateManager.getCurrentQuestion()
        val answer = answerExtractor.extractAnswer(question, currentQuestionView)
        stateManager.saveAnswer(answer)
    }

    private fun showQuizFinishedDialog() {
        AlertDialog.Builder(this)
            .setTitle("Fim das perguntas")
            .setMessage("Você completou todas as perguntas!\nSalve o formulário para anexar o PDF.")
            .setPositiveButton("Salvar e Anexar PDF") { _, _ ->
                
                dataSaver.saveAnswers(stateManager.getFormattedAnswers()) { savedFile ->
                    if (savedFile != null) {

                        // 3. Configure o Manager com os dados atuais
                        pdfManager.currentCsvFile = savedFile
                        pdfManager.currentJwtToken = jwtToken

                        // 4. Inicie a seleção (Isso substitui abrirSeletorDePdf)
                        pdfManager.startPdfSelection()

                    } else {
                        textView.text = "Falha ao salvar CSV. Processo cancelado."
                    }
                }
                
                //dataSaver.saveAnswers(stateManager.getFormattedAnswers())

                stateManager.reset()
                showCurrentQuestion()
            }
            .setNegativeButton("Cancelar", null)
            .create()
            .show()
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == PermissionManager.AUDIO_PERMISSION_REQUEST_CODE) {
            if (grantResults.isEmpty() || grantResults[0] != android.content.pm.PackageManager.PERMISSION_GRANTED) {
                Toast.makeText(this, "A permissão de áudio é necessária para o app funcionar", Toast.LENGTH_LONG).show()
                // Você pode desabilitar o botão de falar aqui
                btnFalar.isEnabled = false
            }
        }
    }

    private fun mostraInstrucoes() {
        val alert = AlertDialog.Builder(this)
            .setTitle("Como Utilizar o aplicativo")
            .setMessage("Aperte o botão 'Falar' e pronuncie a informação referente ao campo mostrado na parte superior da tela.\n" +
                    "Caso necessário, utilize o teclado virtual para eventuais correções ou marcações para campos objetivos")
            .setPositiveButton("Fechar") { _, _ ->
                
            }
            //.setNegativeButton("Não enviar agora", null)
            .create()

        alert.show()
    }
    private fun configurarCliquesNosInputs(view: View) {
        // Se a view for um EditText, configura o clique
        if (view is EditText) {
            view.setOnClickListener {
                campoSelecionado = view // Marca este campo como o alvo da voz
                voiceRecognizer.startListening()
                //Toast.makeText(this, "Ouvindo para: ${view.hint ?: "este campo"}", Toast.LENGTH_SHORT).show()
            }
        }
        // Se for um container (LinearLayout/Group), procura dentro dele (Recursivo)
        else if (view is ViewGroup) {
            for (i in 0 until view.childCount) {
                configurarCliquesNosInputs(view.getChildAt(i))
            }
        }
    }


    override fun onDestroy() {
        super.onDestroy()
        voiceRecognizer.destroy() // Libera recursos do SpeechRecognizer
    }
}