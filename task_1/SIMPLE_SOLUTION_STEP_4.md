After extracted the topics in the <conference-short-name>.jsonl file in the data/topics/ folder, we can now do a bit of data exploration.

For an initial PoC version, lets create a new folder called step4/ and in it a jupyter notebook to do some basic cluster and topic analysis. For embedding the textual content, let's use the EmbeddingGemma-300M-medical model [2,3]. It was fine-tuned on 100,000 medical question–passage pairs from the Medical Instruction and Retrieval Dataset (i.e., specifically to retrieve passages from scientific medical papers). We can download the model in terminal as follows:

`ollama pull hf.co/dontia/embeddinggemma-300m-medical-Q8_0-GGUF:Q8_0`

After analysing the output of topic and cluster analysis, we would involve human experts from the medical field to assess what data does make or not make sense and to come up with solutions to fix it. This will then form the basis for our ground truth approach.


[2] Schechter Vera, H., Dua, S., Zhang, B., Salz, D., Mullins, R., Panyam, S. R., Smoot, S., Naim, I., Zou, J., Chen, F., Cer, D., Lisak, A., Choi, M., Gonzalez, L., Sanseviero, O., Cameron, G., Ballantyne, I., Black, K., Chen, K., . . . Seyedhosseini, M. (2025). EmbeddingGemma: Powerful and lightweight text representations. arXiv. https://doi.org/10.48550/arXiv.2509.20354

[3] https://huggingface.co/blog/embeddinggemma#finetuned-evaluation