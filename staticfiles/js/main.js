document.addEventListener('DOMContentLoaded', function () {

    // Navbar ombre au scroll
    var navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function () {
            navbar.classList.toggle('scrolled', window.scrollY > 10);
        });
    }

    // Si "poste actuel" coché → désactiver date de fin
    var casePosteActuel = document.getElementById('id_poste_actuel');
    var champDateFin = document.getElementById('id_date_fin');
    if (casePosteActuel && champDateFin) {
        function basculerDateFin() {
            champDateFin.disabled = casePosteActuel.checked;
            if (casePosteActuel.checked) champDateFin.value = '';
        }
        casePosteActuel.addEventListener('change', basculerDateFin);
        basculerDateFin();
    }

    // OTP : seulement des chiffres
    var champOtp = document.querySelector('input[name="code"][maxlength="6"]');
    if (champOtp) {
        champOtp.addEventListener('input', function () {
            this.value = this.value.replace(/[^0-9]/g, '').slice(0, 6);
        });
    }

    // Fermer les alertes après 5 secondes
    document.querySelectorAll('.alert-dismissible').forEach(function (alerte) {
        setTimeout(function () {
            var bs = bootstrap.Alert.getOrCreateInstance(alerte);
            if (bs) bs.close();
        }, 5000);
    });

});