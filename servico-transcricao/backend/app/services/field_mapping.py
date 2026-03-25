# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 Lapsi/Fala-texto
"""
CSV-to-PDF field mapping for the surgical safety checklist.

This module contains the domain-specific logic that translates key/value
pairs from the uploaded CSV file into the PDF form field keys expected by
:func:`~app.services.pdf_service.preencher_campos_pdf`.

Keeping the mapping here (rather than inline in a route handler) makes it
independently readable, testable, and editable without touching HTTP logic.
"""

from typing import Any, Dict, Optional


def map_csv_to_pdf_fields(
    dicionario: Dict[str, str],
    campos: Dict[str, Optional[str]],
) -> Dict[str, Any]:
    """Map CSV key/value pairs to PDF form field keys.

    Iterates over every ``(csv_key, csv_value)`` pair and every PDF field
    key and applies the checklist-specific matching rules to decide which
    fields to populate.

    Args:
        dicionario: ``{csv_key: csv_value}`` dict read from the uploaded CSV.
        campos: ``{"field_name|field_type": None}`` dict from
            :func:`~app.services.pdf_service.listar_campos_pdf`.

    Returns:
        ``{"field_name|field_type": value}`` dict ready to be passed to
        :func:`~app.services.field_mapping.coerce_field_types`.
    """
    form: Dict[str, Any] = {}

    for c, v in dicionario.items():
        if v == '':
            continue
        for chave in campos.keys():
            n_campo = chave.split("|")
            if c.lower() == 'nome:' and n_campo[0] == 'nome do paciente':
                form[chave] = v
            elif c.lower() == 'paciente confirmou:':
                if n_campo[0] == 'identidade' and 'Identidade' in v:
                    form[chave] = True
                if n_campo[0] == 'sítio cirúrgico' and 'Sítio Cirúrgico' in v:
                    form[chave] = True
                if n_campo[0] == 'marcar procedimento' and 'Procedimento' in v:
                    form[chave] = True
                if n_campo[0] == 'consentimento' and 'Consentimento' in v:
                    form[chave] = True
            elif c.lower() == 'verificação da segurança anestésica:' or c == 'Verificação da segurança anestésica (Outro):':
                if n_campo[0] == 'montagem da so de acordo com o procedimento' and 'Montagem da SO de acordo com o procedimento' in v:
                    form[chave] = True
                if n_campo[0] == 'material anestésico disponível' and 'Material anestésico disponível' in v:
                    form[chave] = True
                if n_campo[0] == 'outro':
                    form[chave] = v
            elif c.lower() == 'data:' and n_campo[0] == 'data':
                form[chave] = v
            elif c == 'Sítio demarcado (lateralidade):':
                if v.lower() == 'sim' and n_campo[0] == 'sítio demarcado sim':
                    form[chave] = True
                elif v.lower() == 'não' and n_campo[0] == 'sítio demarcado não':
                    form[chave] = True
                elif v.lower() == 'não se aplica' and n_campo[0] == 'não se aplica sítio demarcado':
                    form[chave] = True
            elif c == 'Via aérea difícil/broncoaspiração:':
                if v.lower() == 'sim' and n_campo[0] == 'via aérea difícil sim':
                    form[chave] = True
                elif v.lower() == 'não' and n_campo[0] == 'via aérea difícil não':
                    form[chave] = True
            elif c == 'Risco de grande perda sanguínea superior a 500 ml ou mais 7 ml/kg em crianças:':
                if 'sim' in v.lower() and n_campo[0] == 'risco de grande perda sanguínea sim':
                    form[chave] = True
                elif 'não' in v.lower() and n_campo[0] == 'risco de grande perda sanguínea não':
                    form[chave] = True
                if 'reserva de sangue disponível' in v.lower() and n_campo[0] == 'reserva de sangue disponível':
                    form[chave] = True
            elif c == 'Acesso venoso adequado e pérvio:':
                if 'sim' == v.lower() and n_campo[0] == 'acesso venoso adequado sim':
                    form[chave] = True
                elif 'não' == v.lower() and n_campo[0] == 'acesso venoso adequado não':
                    form[chave] = True
                elif 'providenciado na so' == v.lower() and n_campo[0] == 'acesso venoso adequado providenciado':
                    form[chave] = True
            elif c == 'Histórico de reação alérgica:':
                if v.lower() == 'sim' and n_campo[0] == 'histórico de reação alérgica sim':
                    form[chave] = True
                elif v.lower() == 'não' and n_campo[0] == 'histórico de reação alérgica não':
                    form[chave] = True
            elif c == 'Apresentação oral de cada membro da equipe pelo nome e função:':
                if v.lower() == 'sim' and n_campo[0] == 'apresentação oral sim':
                    form[chave] = True
                elif v.lower() == 'não' and n_campo[0] == 'apresentação oral não':
                    form[chave] = True
            elif c == 'Cirurgião, o anestesista e equipe de enfermagem confirmam verbalmente: Nome do paciente, sítio cirúrgico e procedimento a ser realizado.':
                if v.lower() == 'sim' and n_campo[0] == 'confirmam verbalmente sim':
                    form[chave] = True
                elif v.lower() == 'não' and n_campo[0] == 'confirmam verbalmente não':
                    form[chave] = True
            elif c == 'Antibiótico profilático:':
                if 'sim' == v.lower() and n_campo[0] == 'antibiótico profilático sim':
                    form[chave] = True
                elif 'não' == v.lower() and n_campo[0] == 'antibiótico profilático não':
                    form[chave] = True
                elif 'não se aplica' == v.lower() and n_campo[0] == 'não se aplica antibiótico profilático':
                    form[chave] = True
            elif c == 'Revisão do cirurgião. Momentos críticos do procedimento, tempos principais, riscos, perda sanguínea.:':
                if v.lower() == 'sim' and n_campo[0] == 'revisão do cirurgião sim':
                    form[chave] = True
                elif v.lower() == 'não' and n_campo[0] == 'revisão do cirurgião não':
                    form[chave] = True
            elif c == 'Revisão do anestesista. Há alguma preocupação em relação ao paciente?':
                if v.lower() == 'sim' and n_campo[0] == 'revisão do anestesista sim':
                    form[chave] = True
                elif v.lower() == 'não' and n_campo[0] == 'revisão do anestesista não':
                    form[chave] = True
            elif c == 'Revisão da enfermagem. Correta esterilização do material cirúrgico com fixação dos integradores ao prontuário.':
                if v.lower() == 'sim' and n_campo[0] == 'correta esterilização sim':
                    form[chave] = True
                elif v.lower() == 'não' and n_campo[0] == 'correta esterilização não':
                    form[chave] = True
            elif c == 'Revisão da enfermagem. Placa de eletrocautério posicionada:':
                if v.lower() == 'sim' and n_campo[0] == 'placa de eletrocautério sim':
                    form[chave] = True
                elif v.lower() == 'não' and n_campo[0] == 'placa de eletrocautério não':
                    form[chave] = True
            elif c == 'Revisão da enfermagem. Equipamentos disponíveis e funcionantes:':
                if v.lower() == 'sim' and n_campo[0] == 'equipamentos disponíveis sim':
                    form[chave] = True
                elif v.lower() == 'não' and n_campo[0] == 'equipamentos disponíveis não':
                    form[chave] = True
            elif c == 'Revisão da enfermagem. Insumos e instrumentais disponíveis:':
                if v.lower() == 'sim' and n_campo[0] == 'insumos e instrumentais sim':
                    form[chave] = True
                elif v.lower() == 'não' and n_campo[0] == 'insumos e instrumentais não':
                    form[chave] = True
            elif c == 'Confirmação do procedimento realizado.':
                if v.lower() == 'sim' and n_campo[0] == 'confirmação do procedimento sim':
                    form[chave] = True
                elif v.lower() == 'não' and n_campo[0] == 'confirmação do procedimento não':
                    form[chave] = True
            elif c == 'Contagem de compressas.':
                if v.lower() == 'sim' and n_campo[0] == 'contagem de compressas sim':
                    form[chave] = True
                elif v.lower() == 'não' and n_campo[0] == 'contagem de compressas não':
                    form[chave] = True
                elif 'não se aplica' == v.lower() and n_campo[0] == 'não se aplica contagem de compressas':
                    form[chave] = True
            elif c == 'Compressas entregues:' and n_campo[0] == 'contagem de compressas entregues':
                form[chave] = v
            elif c == 'Compressas conferidas:' and n_campo[0] == 'contagem de compressas conferidas':
                form[chave] = v
            elif c == 'Contagem de instrumentos.':
                if v.lower() == 'sim' and n_campo[0] == 'contagem de instrumentos sim':
                    form[chave] = True
                elif v.lower() == 'não' and n_campo[0] == 'contagem de instrumentos não':
                    form[chave] = True
                elif 'não se aplica' == v.lower() and n_campo[0] == 'não se aplica contagem de instrumentos':
                    form[chave] = True
            elif c == 'Instrumentos entregues:' and n_campo[0] == 'contagem de instrumentos entregues':
                form[chave] = v
            elif c == 'Instrumentos conferidos:' and n_campo[0] == 'contagem de instrumentos conferidos':
                form[chave] = v
            elif c == 'Contagem de agulhas.':
                if v.lower() == 'sim' and n_campo[0] == 'contagem de agulhas sim':
                    form[chave] = True
                elif v.lower() == 'não' and n_campo[0] == 'contagem de agulhas não':
                    form[chave] = True
                elif 'não se aplica' == v.lower() and n_campo[0] == 'não se aplica contagem de agulhas':
                    form[chave] = True
            elif c == 'Agulhas entregues:' and n_campo[0] == 'contagem de agulhas entregues':
                form[chave] = v
            elif c == 'Agulhas conferidas:' and n_campo[0] == 'contagem de agulhas conferidas':
                form[chave] = v
            elif c == 'Amostra cirúrgica identificada adequadamente:':
                if v.lower() == 'sim' and n_campo[0] == 'amostra cirúrgica identificada sim':
                    form[chave] = True
                elif v.lower() == 'não' and n_campo[0] == 'amostra cirúrgica identificada não':
                    form[chave] = True
                elif 'não se aplica' == v.lower() and n_campo[0] == 'não se aplica amostra cirúrgica identificada':
                    form[chave] = True
            elif c == 'Problema com equipamentos que deve ser solucionado:':
                if v.lower() == 'sim' and n_campo[0] == 'problema com equipamentos sim':
                    form[chave] = True
                elif v.lower() == 'não' and n_campo[0] == 'problema com equipamentos não':
                    form[chave] = True
                elif 'não se aplica' == v.lower() and n_campo[0] == 'não se aplica problema com equipamentos':
                    form[chave] = True
            elif c == 'Comunicado a enfermeira para providenciar a solução:' and n_campo[0] == 'comunicado à enfermeira':
                form[chave] = v
            elif c == 'Recomendações Cirurgião:' and n_campo[0] == 'comentário do cirurgião':
                form[chave] = v
            elif c == 'Recomendações Anestesista:' and n_campo[0] == 'comentário da anestesista':
                form[chave] = v
            elif c == 'Recomendações Enfermagem:' and n_campo[0] == 'comentário da enfermagem':
                form[chave] = v
            elif n_campo[0] in c.lower() and n_campo[0] != 'data':
                form[chave] = v

    return form


def coerce_field_types(form: Dict[str, Any]) -> Dict[str, Any]:
    """Convert PDF widget type codes to Python types.

    PDF form fields are keyed as ``"field_name|field_type_int"``.  This
    function strips the type suffix and casts each value to the appropriate
    Python type:

    * ``|7`` → ``str``
    * ``|5`` → ``int``
    * ``|2`` → ``bool``

    Args:
        form: Raw form dict from :func:`map_csv_to_pdf_fields` (keys still
            contain the ``|type`` suffix).

    Returns:
        Dict of ``{field_name: typed_value}`` ready for
        :func:`~app.services.pdf_service.preencher_campos_pdf`.
    """
    data: Dict[str, Any] = {}
    for key, val in form.items():
        if key == "file":
            continue
        name, t = key.split("|")
        t = int(t)
        if t == 7:
            data[name] = val
        elif t == 5:
            data[name] = int(val)
        elif t == 2:
            data[name] = bool(val)
    return data
