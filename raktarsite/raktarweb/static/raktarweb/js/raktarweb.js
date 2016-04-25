function myBruttoCalculations() {
    var brutto_egysar, netto_egysar, afa, mennyiseg, netto_ertek, afa_ertek, brutto_ertek;
    brutto_egysar = document.getElementById("id_brutto").value;
    afa = document.getElementById("id_afa").value;
    mennyiseg = document.getElementById("id_mennyiseg").value;
    kedvezmeny = document.getElementById("id_kedvsz").value;
    netto_egysar = brutto_egysar / (100 + Number(afa)) * 100;
    netto_ertek = Number(mennyiseg)*netto_egysar*(100-Number(kedvezmeny))/100;
    afa_ertek = netto_ertek*afa/100;
    brutto_ertek = netto_ertek+afa_ertek;
    document.getElementById("id_netto").value = netto_egysar.toFixed(2);
    document.getElementById("id_nettoertek").value = netto_ertek.toFixed(0);
    document.getElementById("id_afaertek").value = afa_ertek.toFixed(0);
    document.getElementById("id_bruttoertek").value = brutto_ertek.toFixed(0);
}

function myCheckIfSelectedDropDown(id){
var vevo = document.getElementById(id);
if(vevo.selectedIndex == 0) {
     alert('Válasszon vevőt !!!!!!');}}
