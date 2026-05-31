function printDiv(divId) {
    const content = document.getElementById(divId).innerHTML;

    const originalContent = document.body.innerHTML;
    
    document.body.innerHTML = content;
    
    window.print();
    
    document.body.innerHTML = originalContent;
    
    location.reload();
}