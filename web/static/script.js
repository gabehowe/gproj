'use strict'
fetch('/data').then(response =>
    response.json()
).then(function (data) {
    whenData(data)
})

let currentSorter = ''

class Thing {
    constructor(title, creation, languages, categories, path) {
        this.title = title
        this.creation = creation.replace('00:00:00 GMT', '')
        this.languages = languages
        this.categories = categories
        this.path = path
    }

    create(table) {
        let row = document.createElement('tr')
        table.querySelector('tbody').appendChild(row)
        let cell = row.insertCell()
        cell.appendChild(document.createTextNode(this.title))
        cell = row.insertCell()
        cell.appendChild(document.createTextNode(this.creation))
        cell = row.insertCell()
        for (let i of this.languages) {
            let languageItem = document.createElement('p')
            languageItem.classList.add('obj', 'unselectable')
            languageItem.innerText = i
            cell.appendChild(languageItem)

        }
        cell = row.insertCell()
        for (let i of this.categories) {
            let languageItem = document.createElement('p')
            languageItem.classList.add('obj', 'unselectable')
            languageItem.innerText = i
            cell.appendChild(languageItem)
        }
        cell = row.insertCell()
        let a = document.createElement('a')
        a.href = '/project/' + this.title.toLowerCase()
        a.innerText = '...' + this.title + '\\.gproj'
        cell.appendChild(a)

    }
}

document.querySelectorAll('.taglink').forEach(a => {
    a.addEventListener('click', function (e) {
        e.preventDefault()
        sortByLabel(a.innerText)
    })
})

function sortByLabel(label) {
    if (label === 'Clear') {
        for (let i of document.querySelectorAll('.invisible')) {
            i.classList.remove('invisible')
        }
        document.querySelector('h3').innerText = ""
        currentSorter = ''
        return
    }
    if (currentSorter === label) {
        for (let i of document.getElementsByClassName('invisible')) {
            i.classList.remove('invisible')
        }
        document.querySelector('h3').innerText = ""

        for (let i of document.getElementsByClassName('invisible')) {
            let parentElement = i.parentElement
            i.parentElement.removeChild(i)
            parentElement.appendChild(i)

        }
        return
    }
    let count = 0
    let table = document.querySelector('table')
    let rows = table.rows
    for (let i = 1; i < rows.length; i++) {
        let cells = rows[i].cells
        let found = false
        for (let j = 2; j < cells.length; j++) {
            let cell = cells[j]
            for (let k = 0; k < cell.children.length; k++) {
                if (cell.children[k].innerText === label) {
                    found = true
                    break
                }
            }
            if (found) {
                count += 1
                break
            }
        }
        if (!found) {
            rows[i].classList.add('invisible')
        } else {
            rows[i].classList.remove('invisible')
        }
    }
    for (let i of document.querySelectorAll('tr')) {
        if (i.classList.contains('invisible')) {
            continue
        }
        let parentElement = i.parentElement
        let element = parentElement.removeChild(i)
        parentElement.appendChild(element)

    }
    document.querySelector('h3').innerText = "Found " + count + " items with label " + label + "."
    currentSorter = label
}

function whenData(data) {
    let table = document.querySelector('table')
    for (let i in data) {
        let obj = new Thing(data[i].title, data[i].creation, data[i].languages, data[i].categories, data[i].path)
        obj.create(table)
    }
}